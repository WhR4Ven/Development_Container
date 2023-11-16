#!/bin/bash
# Copyright 2022 Proyectos y Sistemas de Mantenimiento SL (eProsima).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Exit on command failure
set -e

print_usage()
{
    echo "-----------------------------------------------------"
    echo "Bootstrap script for building and installing Fast DDS"
    echo "-----------------------------------------------------"
    echo "GENERAL FLAGS:"
    echo "   -h | --help                 Print help"
    echo "   --no-install-dependencies   Do not install apt dependencies"
    echo "   --no-shared-libs            Do not compile shared libraries"
    echo "   --no-static-libs            Do not compile static libraries. This option is"
    echo "                               incompatible with '--no-shared-libs'"
    echo "   --build-cores               Number of cores used to build. Passed to CMake with -j"
    echo "                               [Defaults: 1]"
    echo ""
    echo "FAST DDS RELATED FLAGS:"
    echo "   --no-security               Do not compile Fast DDS with security support"
    echo "   --install-examples          Build and install Fast DDS examples"
    echo ""
    echo "GENERAL OPTIONAL ARGUMENTS:"
    echo "   --install-prefix   [directory]   The installation directory [Defaults: /usr/local]"
    echo ""
    exit ${1}
}

parse_options()
{
    INSTALL_DEPENDENCIES="TRUE"
    COMPILE_SHARED_LIBS="TRUE"
    COMPILE_STATIC_LIBS="TRUE"
    SECURITY="ON"
    INSTALL_PREFIX="/usr/local"
    INSTALL_EXAMPLES="OFF"
    BUILD_CORES="1"

    # Validate options
    if ! options=$(getopt \
        --name 'install.sh' \
        --options h \
        --longoption \
            help,no-install-dependencies,no-shared-libs,no-static-libs,no-security,install-examples,build-cores:,install-prefix: \
        -- "$@")
    then
        print_usage 1
    fi

    eval set -- "${options}"

    while true
    do
        case "${1}" in
            # General flags
            -h | --help                     ) print_usage 0;;
            --no-install-dependencies       ) INSTALL_DEPENDENCIES="FALSE"; shift;;
            --no-shared-libs                ) COMPILE_SHARED_LIBS="FALSE"; shift;;
            --no-static-libs                ) COMPILE_STATIC_LIBS="FALSE"; shift;;
            --build-cores                   ) BUILD_CORES="${2}"; shift 2;;
            # Fast DDS related flags
            --no-security                   ) SECURITY="OFF"; shift;;
            --install-examples              ) INSTALL_EXAMPLES="ON"; shift;;
            # General optional arguments
            --install-prefix                ) INSTALL_PREFIX="${2}"; shift 2;;
            # End mark
            -- ) shift; break ;;
            # Wrong args
            * ) echo "Unknown option: '${1}'" >&2; print_usage 1;;
        esac
    done

    if [ ${COMPILE_SHARED_LIBS} == "FALSE" ] && [ ${COMPILE_STATIC_LIBS} == "FALSE" ]
    then
        echo "Cannot use both '--no-shared-libs' and '--no-static-libs'"
        print_usage 1
    fi

    SHARED_LIBS_OPTIONS=""
    if [[ ${COMPILE_SHARED_LIBS} == "TRUE" ]]
    then
        SHARED_LIBS_OPTIONS="ON"
    fi

    if [[ ${COMPILE_STATIC_LIBS} == "TRUE" ]]
    then
        SHARED_LIBS_OPTIONS="${SHARED_LIBS_OPTIONS} OFF"
    fi

    if ! test "${BUILD_CORES}" -gt 0 2> /dev/null
    then
        echo "Value '${BUILD_CORES}' passed with --build-cores is not a possitive integer"
        print_usage 1
    fi

    if [[ ! -d ${INSTALL_PREFIX} ]]
    then
        mkdir -p ${INSTALL_PREFIX}
    fi
}

main()
{
    parse_options ${@}

    SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

    # Determine if apt-get is available
    if [[ ${INSTALL_DEPENDENCIES} == "TRUE" ]]
    then
        # Install dependencies
        apt update
        apt install --yes --no-install-recommends \
            git \
            build-essential \
            cmake \
            libssl-dev \
            libasio-dev \
            libtinyxml2-dev \
            openjdk-11-jre-headless \
            python3
    fi

    # Build and install foonthan memory
    mkdir -p ${SCRIPT_DIR}/build/foonathan_memory_vendor
    cd ${SCRIPT_DIR}/build/foonathan_memory_vendor
    cmake \
        -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
        ${SCRIPT_DIR}/src/foonathan_memory_vendor
    cmake --build . --target install -j ${BUILD_CORES}
    cd -

    for SHARED_LIBS_OPTION in ${SHARED_LIBS_OPTIONS}
    do
        # Build and install Fast CDR
        mkdir -p ${SCRIPT_DIR}/build/fastcdr
        cd ${SCRIPT_DIR}/build/fastcdr
        cmake \
            -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
            -DBUILD_SHARED_LIBS=${SHARED_LIBS_OPTION} \
            ${SCRIPT_DIR}/src/fastcdr
        cmake --build . --target install -j ${BUILD_CORES}
        cd -

        # Build and install Fast DDS
        mkdir -p ${SCRIPT_DIR}/build/fastrtps
        cd ${SCRIPT_DIR}/build/fastrtps
        cmake \
            -DCMAKE_PREFIX_PATH=${INSTALL_PREFIX} \
            -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
            -DBUILD_SHARED_LIBS=${SHARED_LIBS_OPTION} \
            -DSECURITY=${SECURITY} \
            -DCOMPILE_EXAMPLES=${INSTALL_EXAMPLES} \
            -DINSTALL_EXAMPLES=${INSTALL_EXAMPLES} \
            ${SCRIPT_DIR}/src/fastrtps
        cmake --build . --target install -j ${BUILD_CORES}
        cd -

        # Remove build directories
        rm -rf ${SCRIPT_DIR}/build
    done

    # Install Fast DDS-Gen
    mkdir -p ${INSTALL_PREFIX}/share/fastddsgen/java
    cp ${SCRIPT_DIR}/java/fastddsgen.jar ${INSTALL_PREFIX}/share/fastddsgen/java
    cp ${SCRIPT_DIR}/java/fastddsgen ${INSTALL_PREFIX}/bin/
    cp -r ${SCRIPT_DIR}/doc/ ${INSTALL_PREFIX}/share/fastrtps/
}

main ${@}
