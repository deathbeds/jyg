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
...                     --config    ${ROOT}${/}atest${/}fixtures${/}jupyter_config.json
...                     --no-browser
...                     --debug
${BOARD_TEMPLATE}       <button data-command-id="${CMD_ID_LICENSES}">Show Licenses</button>


*** Keywords ***
Set Up Lab Suite
    [Documentation]    Ensure a testable server is running
    [Timeout]    30s
    ${port} =    Get Unused Port
    ${base_url} =    Set Variable    /@rf/
    ${token} =    UUID4
    Create Directory    ${LOG_DIR}
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
    Initialize Settings
    Set Window Size    1366    768
    Reload Page
    Wait For JupyterLab Splash Screen

Initialize Settings
    [Documentation]    Configure the plugin
    [Timeout]    10s
    ${boards} =    Create Boards
    Disable JupyterLab Modal Command Palette
    # hangs on windows?
    # Set JupyterLab Plugin Settings    @deathbeds/jyg    boards
    # ...    boards=${boards}
    # ...    enabled=${TRUE}
    # Set JupyterLab Plugin Settings    @deathbeds/jyg    window-proxy    enabled=${TRUE}

Create Boards
    [Documentation]    Create some boards
    ${board} =    Create Dictionary    title=License Board    template=${BOARD_TEMPLATE}
    &{boards} =    Create Dictionary    license-board=${board}
    RETURN    ${boards}

Tear Down Lab Suite
    [Documentation]    Do clean up stuff
    Maybe Accept A JupyterLab Prompt
    Maybe Open JupyterLab Sidebar    File Browser
    Maybe Accept A JupyterLab Prompt
    Click Element    css:${CSS_LAB_FILES_HOME}
    Execute JupyterLab Command    Close All Tabs
    Execute JupyterLab Command    Shut Down All Kernels
    Reset JupyterLab And Close With Coverage
