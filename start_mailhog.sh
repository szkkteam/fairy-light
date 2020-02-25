#!/bin/bash

echo "Starting mailhog ..."

mailhog -api-bind-addr 127.0.0.1:8025 -ui-bind-addr 127.0.0.1:8025 -smtp-bind-addr 127.0.0.1:1025