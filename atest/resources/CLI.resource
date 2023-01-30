*** Settings ***
Documentation       The jyg CLI.

Library             Process
Resource            ./Variables.resource
Resource            ./Screenshots.resource


*** Variables ***
${NEXT_CLI_PROC}    ${0}
@{CLI_COV_ARGS}     coverage
...                 run
...                 --append
...                 --context    robot-cli
...                 --data-file    ${OUTPUT_DIR}${/}.cli.coverage
...                 --branch
...                 --source    jyg
...                 -m
...                 jyg


*** Keywords ***
Start Jyg CLI
    [Documentation]    Start the jyg CLI under coverage.
    [Arguments]    @{argv}
    ${alias} =    Get Next CLI Alias
    ${proc} =    Start Process    @{CLI_COV_ARGS}    @{argv}    alias=${alias}    env:HOME=${FAKE_HOME}
    RETURN    ${proc}

Run Jyg CLI
    [Documentation]    Run the jyg CLI under coverage.
    [Arguments]    @{argv}    ${returncode}=${0}
    ${proc} =    Start Jyg CLI    @{argv}
    ${alias} =    Get Current CLI Alias
    ${rc} =    Wait For Process    ${proc}
    ${result} =    Get Process Result    ${alias}
    Should Be Equal As Integers    ${rc.rc}    ${returncode}    stderr:\n${result.stdout}\nstdout:\n${result.stderr}
    RETURN    ${result}

Get Current CLI Alias
    [Documentation]    Get the currently-running process alias.
    ${alias} =    Set Variable    cli-${NEXT_CLI_PROC}
    RETURN    ${alias}

Get Next CLI Alias
    [Documentation]    Get a new process alias.
    Set Global Variable    ${NEXT_CLI_PROC}    ${NEXT_CLI_PROC.__add__(1)}
    ${alias} =    Get Current CLI Alias
    RETURN    ${alias}
