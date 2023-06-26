#!/bin/bash

RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`

cd build
cmake ..
if [ $? -ne 0 ]; then
echo "${RED}CMake build failed${RESET}"
exit 1
fi
make all
if [ $? -ne 0 ]; then
echo "${RED}Build failed${RESET}"
exit 1
fi
echo "${GREEN}Build successful ! Running the binary...${RESET}"
cd ..
./build/Raycasting