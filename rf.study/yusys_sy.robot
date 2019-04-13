*** Settings ***
Documentation     下载公司损益数据
resource          yusys_resource.robot
Suite Setup       连接网页
# Suite Teardown    退出

*** Variables ***
${Y_M}        2019-03
${DATADIR}    F:/workspace/python/data/${Y_M}


*** Test Cases ***
# 登录
#     Title Should Start With    资源管理
#     Input Text       identifier:loginname   ${用户名}
#     Input Text       identifier:password    ${密码}
#     ${checkcode}=    Get Value From User    输入验证码        default_value=
#     Input Text       identifier:checkcode   ${checkcode}
#     Click Button     login_btn
#     Wait Until Element Is Enabled   css:#research-system       60

下载考核、管理损益汇总
    [Template]     完工百分比损益汇总
    ${考核、管理汇总页}       完工百分比法    考核口径    ${Y_M}    二级部    ${downloaddir}    ${DATADIR}
    ${考核、管理汇总页}       完工百分比法    管理口径    ${Y_M}    二级部    ${downloaddir}    ${DATADIR}

下载考核、管理损益明细
    [Template]     完工百分比损益明细
    ${考核、管理明细页}       完工百分比法    考核口径    ${Y_M}    ${downloaddir}    ${DATADIR}
    ${考核、管理明细页}       完工百分比法    管理口径    ${Y_M}    ${downloaddir}    ${DATADIR}

下载验收损益汇总
    [Template]     验收损益汇总
    ${验收法汇总页}       ${Y_M}    一级部    ${downloaddir}    ${DATADIR}
    ${验收法汇总页}       ${Y_M}    二级部    ${downloaddir}    ${DATADIR}

下载验收法明细
    [Template]     验收损益明细
    ${验收法明细页}       ${Y_M}    ${downloaddir}    ${DATADIR}

下载非项目费用明细
    [Template]     非项目费用明细
    ${部门管理明细页}     ${Y_M}    ${downloaddir}    ${DATADIR}
    ${部门闲置明细页}     ${Y_M}    ${downloaddir}    ${DATADIR}
    ${售前、内部管理、产品研发明细页}     ${Y_M}    ${downloaddir}    ${DATADIR}

下载项目投入明细
    [Template]     项目投入明细
    ${主页}     ${Y_M}    ${downloaddir}    ${DATADIR}