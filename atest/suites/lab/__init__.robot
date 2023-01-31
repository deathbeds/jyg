*** Settings ***
Documentation       Tests for JupyterLab.

Library             uuid
Library             JupyterLibrary
Resource            ../../resources/Coverage.resource
Resource            ../../resources/LabSelectors.resource
Resource            ../../resources/Variables.resource
Resource            ../../resources/Screenshots.resource
Resource            ../../resources/Commands.resource

Suite Setup         Set Up Lab Suite
Suite Teardown      Tear Down Lab Suite

Test Tags           app:lab


*** Variables ***
${LOG_DIR}              ${OUTPUT_DIR}${/}logs
@{LAB_COV_ARGS}         run
...                     --append
...                     --context    robot-lab
...                     --data-file    ${OUTPUT_DIR}${/}.lab.coverage
...                     --branch
...                     --source    jyg
...                     -m
@{LAB_ARGS}             jupyterlab
...                     --config    ${FIXTURES}${/}jupyter_config.json
...                     --no-browser
...                     --debug
${BOARD_TEMPLATE}       <button data-command-id="${CMD_ID_LICENSES}">Show Licenses</button>


*** Keywords ***
Set Up Lab Suite
    [Documentation]    Ensure a testable server is running
    ${port} =    Get Unused Port
    ${base_url} =    Set Variable    /@rf/
    ${token} =    UUID4
    Initialize Directories
    Wait For New Jupyter Server To Be Ready
    ...    coverage
    ...    ${port}
    ...    ${base_url}
    ...    ${NONE}    # notebook_dir
    ...    ${token.__str__()}
    ...    @{LAB_COV_ARGS}
    ...    @{LAB_ARGS}
    ...    --port    ${port}
    ...    --ServerApp.token    ${token.__str__()}
    ...    --ServerApp.base_url    ${base_url}
    ...    stdout=${LOG_DIR}${/}lab.log
    ...    env:HOME=${FAKE_HOME}
    Open JupyterLab
    Set Window Size    1920    1080
    Reload Page
    Wait For JupyterLab Splash Screen

Initialize Directories
    [Documentation]    Configure the plugin
    [Timeout]    10s
    Create Directory    ${LOG_DIR}
    Remove Directory    ${USER_SETTINGS}    recursive=${TRUE}
    Copy Directory    ${FIXTURES}${/}user-settings    ${USER_SETTINGS}

Tear Down Lab Suite
    [Documentation]    Do clean up stuff
    Maybe Accept A JupyterLab Prompt
    Maybe Open JupyterLab Sidebar    File Browser
    Maybe Accept A JupyterLab Prompt
    Click Element    css:${CSS_LAB_FILES_HOME}
    Execute JupyterLab Command    Close All Tabs
    Execute JupyterLab Command    Shut Down All Kernels
    Reset JupyterLab And Close With Coverage
