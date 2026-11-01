'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { add } = require('./add.cjs');

test('adds positive values', () => assert.equal(add(2, 3), 5));
test('adds negative values', () => assert.equal(add(-2, -3), -5));
test('adds zero', () => assert.equal(add(0, 7), 7));
