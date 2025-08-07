# Note: no project() call here, inherits from top‑level

# Library target: cellular simulation core
add_library(cell_sim
    # source files
    ${CMAKE_CURRENT_LIST_DIR}/../src/cell.cpp
    ${CMAKE_CURRENT_LIST_DIR}/../src/controller.cpp
    ${CMAKE_CURRENT_LIST_DIR}/../src/grid.cpp
)

# Include headers from the include directory
target_include_directories(cell_sim
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/../include
)

# Executable for demo
add_executable(CellSimDemo
    ${CMAKE_CURRENT_LIST_DIR}/main.cpp
)

# Link demo against the library
target_link_libraries(CellSimDemo
    PRIVATE
        cell_sim
)
# Set output directories
set_target_properties(CellSimDemo cell_sim PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib
)