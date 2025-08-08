# ---
# File: CellSimLib/app/CMakeLists.txt
# ---
# Inherit project settings from top-level

# Library target: cellular simulation core
add_library(cell_sim STATIC
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
        pthread
)

# Set explicit output directories for various target types
set_target_properties(cell_sim PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/lib"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/lib"
)
set_target_properties(CellSimDemo PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin"
)