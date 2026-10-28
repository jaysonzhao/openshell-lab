ARG OPENSHELL_BASE_IMAGE
FROM ${OPENSHELL_BASE_IMAGE}
USER root
ARG COPILOT_VERSION=1.0.105
ENV COPILOT_AUTO_UPDATE=false
RUN test -n "$COPILOT_VERSION" \
    && node -e 'if (Number(process.versions.node.split(".")[0]) < 22) process.exit(1)' \
    && npm_config_ignore_scripts=false npm install --global "@github/copilot@${COPILOT_VERSION}" \
    && copilot --version
COPY demo/ /opt/copilot-demo/
RUN chmod -R a+rX /opt/copilot-demo
USER sandbox
WORKDIR /sandbox
