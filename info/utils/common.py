"""自定义公共的工具类"""


def do_index_class(index):
    """主页排行过滤器"""
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''


def do_index_active(index):
    if index == 1:
        return 'active'
    else:
        return ''
