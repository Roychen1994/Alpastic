
def json_quicksort(array,sortkey,asc=1):
    """
    对json列表使用快速排序法,列表里面套字典那种
    :param array: 需要排序的列表
    :param sortkey: 对列表中哪一个key的值进行排序
    :param asc: “2”的时候是降序,其它都为升序
    :return: 排好顺序的列表
    """
    if len(array) < 2 :
        return array
    else:
        pivot = array[0]
        less = []
        greater = []

        pivotvalue = pivot[sortkey]
        for temparray in array[1:]:
            if temparray[sortkey] <= pivotvalue:
                less.append(temparray)
            else:
                greater.append(temparray)
        if asc == "2":
            return json_quicksort(greater,sortkey,asc) + [pivot] +json_quicksort(less,sortkey,asc)
        else:
            return json_quicksort(less, sortkey, asc) + [pivot] + json_quicksort(greater, sortkey, asc)