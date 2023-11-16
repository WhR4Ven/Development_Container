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

# Do not use sudo for root users.
# IMPORTANT: This needs to be declared before any function that uses it
if [[ ${EUID} == 0 ]]
then
    shopt -s expand_aliases
    alias sudo=""
fi

print_usage()
{
    echo "----------------------------------"
    echo "Uninstallation script for Fast DDS"
    echo "----------------------------------"
    echo "GENERAL FLAGS:"
    echo "   -h | --help                 Print help"
    echo ""
    echo "GENERAL OPTIONAL ARGUMENTS:"
    echo "   --install-prefix   [directory]   The installation directory [Defaults: /usr/local]"
    echo ""
    exit ${1}
}

parse_options()
{
    INSTALL_PREFIX="/usr/local"

    # Validate options
    if ! options=$(getopt \
        --name 'uninstall.sh' \
        --options h \
        --longoption \
            help,install-prefix: \
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
            # General optional arguments
            --install-prefix                ) INSTALL_PREFIX="${2}"; shift 2;;
            # End mark
            -- ) shift; break ;;
            # Wrong args
            * ) echo "Unknown option: '${1}'" >&2; print_usage 1;;
        esac
    done

    if [[ ! $(find ${INSTALL_PREFIX} -iname "libfastrtps*.so") ]]
    then
        echo "'${INSTALL_PREFIX}' does not contain a Fast DDS installation"
        print_usage 0
    fi
}

main()
{
    parse_options ${@}

    # Uninstall Fast CDR
    sudo rm -rf ${INSTALL_PREFIX}/share/fastcdr 2&> /dev/null
    sudo rm -rf ${INSTALL_PREFIX}/include/fastcdr 2&> /dev/null
    sudo rm -rf ${INSTALL_PREFIX}/lib/cmake/fastcdr 2&> /dev/null
    sudo rm ${INSTALL_PREFIX}/lib/libfastcdr.so* 2&> /dev/null
    sudo rm ${INSTALL_PREFIX}/lib/libfastcdr.a 2&> /dev/null

    # Uninstall Fast DDS
    sudo rm -rf ${INSTALL_PREFIX}/share/fastrtps 2&> /dev/null
    sudo rm -rf ${INSTALL_PREFIX}/include/fastrtps 2&> /dev/null
    sudo rm -rf ${INSTALL_PREFIX}/include/fastdds 2&> /dev/null
    sudo rm -rf ${INSTALL_PREFIX}/tools/fastdds 2&> /dev/null
    if [ -z "$(ls -A ${INSTALL_PREFIX}/tools)" ]; then
        sudo rm -rf ${INSTALL_PREFIX}/tools 2&> /dev/null
    fi
    sudo rm ${INSTALL_PREFIX}/lib/libfastrtps.so* 2&> /dev/null
    sudo rm ${INSTALL_PREFIX}/lib/libfastrtps.a 2&> /dev/null
    sudo rm ${INSTALL_PREFIX}/bin/fastdds 2&> /dev/null
    sudo rm ${INSTALL_PREFIX}/bin/fast-discovery-server* 2&> /dev/null
    sudo rm ${INSTALL_PREFIX}/bin/nodesize_dbg 2&> /dev/null
    sudo rm ${INSTALL_PREFIX}/bin/ros-discovery 2&> /dev/null
    sudo rm -rf ${INSTALL_PREFIX}/examples/cpp/dds 2&> /dev/null
    sudo rm -rf ${INSTALL_PREFIX}/examples/cpp/rtps 2&> /dev/null
    if [ -z "$(ls -A ${INSTALL_PREFIX}/examples/cpp)" ]; then
        sudo rm -rf ${INSTALL_PREFIX}/examples/cpp 2&> /dev/null
    fi
    if [ -z "$(ls -A ${INSTALL_PREFIX}/examples)" ]; then
        sudo rm -rf ${INSTALL_PREFIX}/examples 2&> /dev/null
    fi

    # Uninstall Foonathan memory & vendor
    sudo rm -rf ${INSTALL_PREFIX}/share/foonathan_memory 2&> /dev/null
    sudo rm -rf ${INSTALL_PREFIX}/share/foonathan_memory_vendor 2&> /dev/null
    sudo rm -rf ${INSTALL_PREFIX}/include/foonathan_memory 2&> /dev/null
    sudo rm -rf ${INSTALL_PREFIX}/lib/foonathan_memory 2&> /dev/null
    sudo rm ${INSTALL_PREFIX}/lib/libfoonathan_memory* 2&> /dev/null

    # Uninstall Fast DDS-Gen
    sudo rm ${INSTALL_PREFIX}/bin/fastddsgen 2&> /dev/null
    sudo rm -rf ${INSTALL_PREFIX}/share/fastddsgen 2&> /dev/null
}

main ${@}
