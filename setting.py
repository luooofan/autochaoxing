# 用户账户
ACCOUNTS = [
  {
    "phone": "",  # 手机号
    "passwd": ""  # 密码
  }
  #,
  #{
  #  "phone": "", # 手机号
  #  "passwd": "" # 密码
  #}
  #...
]

# 刷课模式
# single     单课程自动模式: 选择课程,自动完成该课程
# fullauto   全自动模式:    自动遍历全部课程,无需输入
# control    单课程控制模式: 选择课程并选择控制章节,自动完成[该课程第一个未完成章节,选定章节)范围内章节
# debug      调试模式
MODE = "single"

# 视频倍速
# [0.625, 16]
RATE = 1.0

# 自动答题时,如果未找到答案的题目数量达到num,则暂时保存答案,不提交
# [0, +∞)
NUM = 5