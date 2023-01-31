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

Test Tags           app:lab    server:${jp_app}


*** Variables ***
${LOG_DIR}      ${OUTPUT_DIR}${/}logs


*** Keywords ***
Set Up Lab Suite
    [Documentation]    Ensure a testable server is running
    Initialize Directories
    ${port} =    Get Unused Port
    ${base_url} =    Set Variable    /@rf/
    ${token} =    UUID4
    ${args} =    Get Jupyter App Args    ${port}    ${base_url}    ${token}
    Wait For New Jupyter Server To Be Ready    @{args}
    ...    stdout=${LOG_DIR}${/}${JP_SERVER_APP}.log
    ...    env:HOME=${FAKE_HOME}
    Open JupyterLab
    Set Window Size    1920    1080
    Reload Page
    Wait For JupyterLab Splash Screen

Get Jupyter App Args
    [Documentation]    Build the arguments for the Jupyter Server App
    [Arguments]    ${port}    ${base_url}    ${token}
    ${cfg_app} =    Set Variable    ServerApp
    IF    "${JP_SERVER_APP}" == "notebook"
        ${cfg_app} =    Set Variable    NotebookApp
    END
    @{args} =    Set Variable
    ...    coverage
    ...    ${port}
    ...    ${base_url}
    ...    ${NONE}    # notebook_dir
    ...    ${token.__str__()}
    ...    run
    ...    --append
    ...    --context    robot-${JP_SERVER_APP}
    ...    --data-file    ${OUTPUT_DIR}${/}.${JP_SERVER_APP}.coverage
    ...    --branch
    ...    --source    jyg
    ...    -m    ${JP_SERVER_APP}
    ...    --config    ${FIXTURES}${/}${JP_SERVER_APP}_config.json
    ...    --no-browser
    ...    --debug
    ...    --port    ${port}
    ...    --${cfg_app}.token    ${token.__str__()}
    ...    --${cfg_app}.base_url    ${base_url}
    RETURN    ${args}

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
