#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAW_DIR="${1:-${ROOT_DIR}/../secure-agent-workspace}"
WORKSHOP_COMPONENT="${ROOT_DIR}/content/antora.yml"
SAW_COMPONENT="${SAW_DIR}/docs/antora/antora.yml"
MODULE_DIR="${ROOT_DIR}/content/modules/ROOT/pages"

fail() {
  printf 'Documentation contract error: %s\n' "$1" >&2
  exit 1
}

[[ -f "${WORKSHOP_COMPONENT}" ]] || fail "missing ${WORKSHOP_COMPONENT}"
[[ -f "${SAW_COMPONENT}" ]] || fail "missing ${SAW_COMPONENT}"
[[ ! -e "${ROOT_DIR}/automation/saw" ]] || fail "SAW deployment assets must not be copied into automation/saw"

expected_url="$(ruby -e 'require "yaml"; puts YAML.load_file(ARGV[0]).fetch("content").fetch("sources").find { |source| source["start_path"] == "docs/antora" }.fetch("url")' "${ROOT_DIR}/site.yml")"
expected_branch="$(ruby -e 'require "yaml"; puts YAML.load_file(ARGV[0]).fetch("content").fetch("sources").find { |source| source["start_path"] == "docs/antora" }.fetch("branches")' "${ROOT_DIR}/site.yml")"
actual_branch="$(git -C "${SAW_DIR}" branch --show-current)"
[[ "${actual_branch}" == "${expected_branch}" ]] || fail "SAW checkout is on ${actual_branch}, expected ${expected_branch}"
git -C "${SAW_DIR}" remote -v | awk '{print $2}' | grep -Fxq "${expected_url}" || \
  fail "SAW checkout has no remote matching ${expected_url}"

ruby -e '
  require "yaml"
  workshop = YAML.load_file(ARGV[0]).dig("asciidoc", "attributes")
  saw = YAML.load_file(ARGV[1]).dig("asciidoc", "attributes")
  keys = %w[
    saw_repo_url saw_repo_branch saw_repo_dir saw_namespace saw_gitops_namespace
    saw_gateway_name saw_workspace saw_sandbox openshell_version
    openshell_saw_version ocp_version
  ]
  mismatches = keys.reject { |key| workshop[key] == saw[key] }
  abort "Documentation attributes differ: #{mismatches.join(", ")}" unless mismatches.empty?

  saw_root = File.expand_path(File.join(File.dirname(ARGV[1]), "modules", "ROOT"))
  Dir[File.join(File.dirname(ARGV[0]), "modules", "ROOT", "pages", "*.adoc")].each do |page|
    content = File.read(page)
    content.scan(/include::secure-agent-workspace:ROOT:partial\$([^\[]+)\[\]/).flatten.each do |relative|
      target = File.join(saw_root, "partials", relative)
      abort "Missing cross-component include #{relative} from #{page}" unless File.file?(target)
    end
    content.scan(/xref:secure-agent-workspace:ROOT:([^\[]+)\[/).flatten.each do |relative|
      target = File.join(saw_root, "pages", relative)
      abort "Missing cross-component xref #{relative} from #{page}" unless File.file?(target)
    end
  end
' "${WORKSHOP_COMPONENT}" "${SAW_COMPONENT}"

required_partials=(
  scope.adoc
  control-node.adoc
  cluster-prerequisites.adoc
  clone-and-secrets.adoc
  install.adoc
  configure-client.adoc
  validate.adoc
  troubleshooting.adoc
)

for partial in "${required_partials[@]}"; do
  test -f "${SAW_DIR}/docs/antora/modules/ROOT/partials/deployment/${partial}"
  grep -Fq "partial\$deployment/${partial}" "${MODULE_DIR}"/*.adoc
done

make_database="$(mktemp)"
trap 'rm -f "${make_database}"' EXIT
make -C "${SAW_DIR}" -qp >"${make_database}" 2>/dev/null || true

required_targets=(
  generate-keys
  copy-images
  login
  openshell-saw-configure-gateway
  openshell-saw-list
  openclaw-tui
  nemoclaw-gui
)

for target in "${required_targets[@]}"; do
  grep -Eq "^${target}:" "${make_database}" || {
    printf 'Missing SAW Make target: %s\n' "${target}" >&2
    exit 1
  }
done

printf 'Documentation contract checks passed.\n'
