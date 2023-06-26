project(Raycasting)

set(SRC_FILES
    ${PROJECT_SOURCE_DIR}/src/mainV2_thread.cpp
)

set(HDR_FILES 
)

# Create my target
add_executable(${PROJECT_NAME} ${HDR_FILES} ${SRC_FILES})

target_link_libraries(Raycasting PRIVATE sfml-graphics sfml-window sfml-system)