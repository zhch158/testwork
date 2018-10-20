*** Settings ***
Documentation     启动selenium远程Webdriver，CHROME(chromedriver.exe)，FIREFOX(geckodriver.exe)
Library           Process
Library           OperatingSystem 
Library           Dialogs
# Suite Setup       启动webdriver       ${chrome}
# Suite Teardown    退出

*** Variables ***
${firefox}      geckodriver.exe
${chrome}       chromedriver.exe
${handle}

*** Test Cases ***
启动chrome driver
    启动单体webdriver     ${chrome}

启动firefox driver
    启动单体webdriver     ${firefox}

*** Keywords ***
启动单体webdriver
    [Arguments]       ${server}
    # ${path}=          Get Environment Variable    PATH
    # Log To Console    ${path}
    ${result}=        Run Process             tasklist.exe | findstr.exe      ${server}     output_encoding=UTF-8        shell=True        alias=myproc
    # ${result}=          Run Process             tasklist.exe             shell=True    alias=myproc
    # Should Not Contain  ${result.stdout}        ${server}
    Log Many            result.rc=${result.rc}  result.stdout=${result.stdout}        result.stderr=${result.stderr}
    # ${result}=        Get Process Result      myproc
    # Run Keyword if      ${result.rc} == 0       ${handle}=              启动webdriver        ${server}
    # Run Keyword if      ${server} in ${result.stdout}       ${handle}=              启动webdriver        ${server}

启动webdriver
    [Arguments]       ${server}
    # ${path}=          Get Environment Variable    PATH
    # Log To Console    ${path}
    ${handle}=        Start Process           ${server}       alias=server_proc
    ${pid}=           Get Process Id          ${handle}
    # ${result}=      Get Process Result      server_proc
    Log Many          server=${server}        handle=${handle}            pid=${pid}

停止webdriver
    # [Arguments]       ${handle}
    # Terminate Process         handle=${handle}        kill=true
    Execute Manual Step        是否终止
    Terminate All Processes    kill=true