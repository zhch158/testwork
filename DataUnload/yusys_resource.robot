*** Settings ***
Documentation     it.yusys.com.cn中的KEYWORD，Variables
Library           ./ExtendedSeleniumLibrary.py      timeout=120.0     implicit_wait=0.5        run_on_failure=Capture Page Screenshot
Library           Dialogs
Library           Screenshot

*** Variables ***
${主页}            http://it.yusys.com.cn/yusys/main.asp
${登录页}          http://it.yusys.com.cn/yusys/login.html
${考核、管理汇总页}    http://it.yusys.com.cn/yusys/DeptProfitAndLossTotal/toList.asp
${验收法汇总页}     http://it.yusys.com.cn/yusys/deptProfitTotal/toList.asp
${考核、管理明细页}    http://it.yusys.com.cn/yusys/DeptProfitAndLossDetail/toList.asp
${验收法明细页}     http://it.yusys.com.cn/yusys/deptProfitDetail/toList.asp
${部门管理明细页}   http://it.yusys.com.cn/yusys/deptBudgetCompareActualTotal/toList.asp
${部门闲置明细页}   http://it.yusys.com.cn/yusys/idleDeptBudgetCompareActualTotal/toList.asp
${售前、内部管理、产品研发明细页}     http://it.yusys.com.cn/yusys/preSalRealContrastTableDetail/toList.asp
${用户名}          zhengchun
${密码}            zhengchun
${downloaddir}    X:${/}TEMP
${浏览器}          Chrome
# ${浏览器}          Firefox
${ff_profile_dir}     F:${/}workspace${/}selenium-profile
${paramsfile}     ./${浏览器}.params.json

*** Keywords ***
打开网页
    [Arguments]     ${url}
    My Open Browser    url=${url}    browser=${浏览器}    remote_url=http://127.0.0.1:9515     downloaddir=${downloaddir}    paramsfile=${paramsfile}
    # My Open Browser    url=${url}    browser=${浏览器}    remote_url=http://127.0.0.1:4444     downloaddir=${downloaddir}    paramsfile=${paramsfile}    ff_profile_dir=${ff_profile_dir} 
    Wait For Condition      return document.readyState=="complete"     60

连接网页
    [Arguments]     
    My Connect Browser    paramsfile=${paramsfile}
    Wait For Condition    return document.readyState=="complete"     60

跳转网页
    [Arguments]     ${url}
    Go to           ${url}
    Wait For Condition      return document.readyState=="complete"     60

选择核算类别
    [Arguments]     ${核算类别}
    Sleep            2
    # Click Element    xpath://div[@id='s2id_accountingmethod']/a/span
    # Click Element    css:#s2id_accountingmethod > a:nth-child(1) > span:nth-child(1)
    # Click Element    css:#s2id_accountingmethod > a.select2-choice > span
    Click Element    css:#s2id_accountingmethod > a > span
    Click Element    css:li.select2-results-dept-0 > div.select2-result-label[title='${核算类别}']

选择报表口径
    [Arguments]     ${报表口径}
    Click Element    css:#s2id_caliber > a.select2-choice > span
    Click Element    css:li.select2-results-dept-0 > div.select2-result-label[title='${报表口径}']

输入查询时间
    [Arguments]     ${查询时间}
    Input Text      identifier:searchtime   ${查询时间}
   
输入查询期间
    [Arguments]     ${查询时间}
    Input Text      identifier:period   ${查询时间}
   
选择项目分类
    [Arguments]     ${项目分类}
    Wait Until Element Is Enabled   css:#s2id_projclassify > a.select2-choice > span       60
    Click Element    css:#s2id_projclassify > a.select2-choice > span
    Click Element    css:li.select2-results-dept-0 > div.select2-result-label[title='${项目分类}']

选择部门类型s2id_categroy
    [Arguments]     ${部门类型}
    Wait Until Element Is Enabled   css:#s2id_categroy > a > span
    Click Element    css:#s2id_categroy > a > span
    Click Element    css:li.select2-results-dept-0 > div.select2-result-label[title='${部门类型}']

选择部门类型
    [Arguments]     ${部门类型}
    Wait Until Element Is Enabled   css:#s2id_orgtype > a > span
    Click Element    css:#s2id_orgtype > a > span
    Click Element    css:li.select2-results-dept-0 > div.select2-result-label[title='${部门类型}']

执行查询
    Click Button     query
    # Wait Until Element Is Enabled     query       120

下载报表-HREF
    [Arguments]                 ${downloaddir}    ${查询时间}        ${保存目录}     ${HREF}
    switch_frame                runqian
    Sleep            2
    # my_wait_until_element_presence   css:img[alt="存为Excel"]       500
    my_wait_until_element_presence   ${HREF}       500
    ${原文件}    ${目标文件}=    Get Report Filename     identifier:saveAsName        ${downloaddir}        ${查询时间}        ${保存目录}
    Delete Report File          ${原文件}          ${目标文件}
    # Click Element               css:img[alt="存为Excel"]
    Click Element               ${HREF}
    Rename File                 ${原文件}          ${目标文件}
    
下载报表结果
    [Arguments]     ${downloaddir}    ${查询时间}        ${保存目录}
    下载报表-HREF    ${downloaddir}    ${查询时间}        ${保存目录}     css:#saveExcelA > img
    
下载项目人月报表结果
    [Arguments]     ${downloaddir}    ${查询时间}        ${保存目录}
    下载报表-HREF    ${downloaddir}    ${查询时间}        ${保存目录}     css:#functionBar > a > img
    
快照
    Capture Page Screenshot           yusys-{index}.png

退出
    # [Teardown]       Close Browser
    Pause Execution
    Close Browser

完工百分比损益汇总
    [Arguments]     ${报表首页}    ${核算类别}    ${报表口径}    ${查询时间}   ${部门类型}    ${downloaddir}    ${保存目录}
    跳转网页         ${报表首页}      
    选择核算类别     ${核算类别}
    选择报表口径     ${报表口径}
    输入查询时间     ${查询时间}
    选择部门类型s2id_categroy     ${部门类型}
    执行查询
    下载报表结果     ${downloaddir}        ${查询时间}        ${保存目录}

验收损益汇总
    [Arguments]     ${报表首页}    ${查询时间}   ${部门类型}    ${downloaddir}    ${保存目录}
    跳转网页         ${报表首页}      
    输入查询期间     ${查询时间}
    选择部门类型     ${部门类型}
    执行查询
    下载报表结果     ${downloaddir}        ${查询时间}        ${保存目录}

完工百分比损益明细
    [Arguments]     ${报表首页}    ${核算类别}    ${报表口径}    ${查询时间}     ${downloaddir}    ${保存目录}
    跳转网页         ${报表首页}      
    选择核算类别     ${核算类别}
    选择报表口径     ${报表口径}
    输入查询时间     ${查询时间}
    # 选择项目分类     ${项目分类}
    执行查询
    下载报表结果     ${downloaddir}        ${查询时间}        ${保存目录}

验收损益明细
    [Arguments]     ${报表首页}    ${查询时间}   ${downloaddir}    ${保存目录}
    跳转网页         ${报表首页}      
    输入查询期间     ${查询时间}
    执行查询
    下载报表结果     ${downloaddir}        ${查询时间}        ${保存目录}

非项目费用明细
    [Arguments]     ${报表首页}    ${查询时间}   ${downloaddir}    ${保存目录}
    跳转网页         ${报表首页}      
    输入查询时间     ${查询时间}
    执行查询
    下载报表结果     ${downloaddir}        ${查询时间}        ${保存目录}

项目投入明细
    [Arguments]     ${报表首页}    ${查询时间}   ${downloaddir}    ${保存目录}
    跳转网页         ${报表首页}
    Click Element   css:#research-system                 #切换应用系统
    Click Element   identifier:xdglxt                    #考勤管理
    Click Element   identifier:Report_Analysis           #考勤报表
    Click Element   identifier:Foundation_Report         #明细类
    Click Element   identifier:Staff_Inputs_Condition    #人员投入情况
    Click Element   identifier:yyglbb3                   #项目投入统计明细表
    switch_frame    yyglbb3-ifr-casually
    my_wait_until_element_presence   name:startDate      60 
    Clear Element Text   identifier:startDate
    Input Text      identifier:startDate   ${查询时间}
    Click Button    button_query                         #执行查询
    下载项目人月报表结果     ${downloaddir}        ${查询时间}        ${保存目录}
