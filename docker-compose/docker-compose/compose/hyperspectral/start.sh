#!/bin/bash
nohup java -jar base_vue_system_core.jar --spring.profiles.active=pro > base_vue_system_core.log 2>&1 &
tail -1000f base_vue_system_core.log
