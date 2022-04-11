from PIL import Image, PngImagePlugin
import numpy as np

def crop_img_idex(mask, begin, stop, order = True):
    if order:
        sequen = 1
    else:
        sequen = -1
    id = 0  # 这里不先赋值 就会报错local variable 'id' referenced before assignment
    for id in range(begin, stop, sequen):
        if mask[id] > 0:
            break
    return id

def whether_to_rm(mask, bottom = False):
    to_rm = True

    if not bottom:
        if mask[1] > 0:
            to_rm = False
            print("无边框可以移除")
    elif bottom:
        if mask[-1] >0:
            to_rm =False
            print("无边框可以移除")
    return to_rm

def remove_one_edge(Img, imarray, top = True, bottom = False, left = False, right = False, diff = False):
    # top 0 h-1 bottom h-1 0 left 0 w-1
    w = Img.width  # 图片的宽
    h = Img.height  # 图片的高
    w_begin, h_begin, w_new, h_new = 0, 0, w, h

    if top or left:
        judge = imarray[0, 0]
    elif bottom == 1 or right:
        judge = imarray[h - 1, w - 1]

    mask = np.sum(imarray != judge, axis=-1) > 0


    if top or bottom:
        mask1 = np.sum(mask, axis=-1)
        if not whether_to_rm(mask1, bottom=bottom):
            return Img
        if top:
            h_begin = crop_img_idex(mask1, 0, h)
            h_begin = h_begin + 1
            print(f"将要剪裁上边界至像素{h_begin}")
        elif bottom:
            h_new = crop_img_idex(mask1, h-1, 0, order=False)
            h_new = h_new - 1
            print(f"将要剪裁下边界至像素{h_new}")
    if left or right:
        mask2 = np.sum(mask, axis=-2)
        if not whether_to_rm(mask2,bottom=right):
            return Img
        if left:
            w_begin = crop_img_idex(mask2, 0, w)
            w_begin = w_begin + 1
            print(f"将要剪裁左边界至像素{w_begin}")
        elif right:
            w_new = crop_img_idex(mask2, w-1, 0,order=False)
            w_new = w_new - 1
            print(f"将要剪裁右边界至像素{w_new}")
    Img = Img.crop((w_begin, h_begin, w_new, h_new))
    return Img

def rm_edges(Img,imarray,edge ):
    w = Img.width  # 图片的宽
    h = Img.height  # 图片的高
    w_begin, h_begin, w_new, h_new = 0, 0, w, h
    if edge.all == np.array([0,1,0,1]).all:
        judge = imarray[h - 1, w - 1]
    else:
        judge = imarray[0, 0]
    mask = np.sum(imarray != judge, axis=-1) > 0
    maskud = np.sum(mask, axis=-1)
    masklr = np.sum(mask, axis=-2)
    if edge[0]==1:
        h_begin = crop_img_idex(maskud, 0, h)
        h_begin = h_begin + 1
        print(f"将要剪裁上边界至像素{h_begin}")
    if edge[1]==1:
        h_new = crop_img_idex(maskud, h - 1, 0, order=False)
        h_new = h_new - 1
        print(f"将要剪裁下边界至像素{h_new}")
    if edge[2]==1:
        w_begin = crop_img_idex(masklr, 0, w)
        w_begin = w_begin + 1
        print(f"将要剪裁左边界至像素{w_begin}")
    if edge[3]==1:
        w_new = crop_img_idex(masklr, w - 1, 0, order=False)
        w_new = w_new - 1
        print(f"将要剪裁右边界至像素{w_new}")
    Img = Img.crop((w_begin, h_begin, w_new, h_new))
    return Img


def remove_edge(img, edge = None, style = "diff"):
    """
    img: 传入图片，格式为PIL格式，np格式，或者是路径
    edge: 为一个list[x,x,x,x] x为0或者1，如果为1则代表去除这条边的边框，顺序分别为上下左右，同时为1的两条边的边界可以是一样的也可以是不一样的，
    默认选项为diff
    style:["same", "diff"],same 表示去除的几个边的框框的像素值需要是一样的，diff表示只要框的一条边上像素值是一样的就可以去除
    当edge没传参的时候,默认按照上下左右顺序，尽可能去掉大宽度的边框
    """
    if type(img) == str:
        img = Image.open(img)
        imarray = np.array(img)
    elif type(img) is np.ndarray:
        imarray = img
        img = Image.fromarray(imarray)
    elif type(img) is PngImagePlugin.PngImageFile:
        imarray = np.array(img)
    else:
        print("对象既不是地址，也不是数组，PngImageFile")
        return 0
    #print(type(edge))
    if type(edge) == list:
        edge = np.array(edge)
    print(  (type(edge) is np.ndarray and (edge.ndim != 1 or edge.shape != (4,))) )
    if (type(edge) is None) and (type(edge) is not np.ndarray  or (type(edge) is np.ndarray and (edge.ndim != 1 or edge.shape != (4,)))):
        print("edge 传入参数错误！")
        return img

    if edge is not None and sum(edge) != sum(edge == 1):
        # 修正edge的数值
        for i in [0, 1, 2, 3]:
            if edge[i]<0:
                edge[i] = 0
            elif edge[i]>0:
                edge[i] = 1
    if edge is not None and sum(edge) == 0:
        print("无需修改")
        return img
    w = img.width  # 图片的宽
    h = img.height  # 图片的高

    if edge is not None and sum(edge) == 1:
        # 这个情况下 无论是diff还是same都是一样的
        img = remove_one_edge(img, imarray, edge[0]==1, edge[1]==1, edge[2]==1, edge[3]==1)
        print(1)
    elif edge is not None and sum(edge) == 2:
        edge1 = edge.reshape(2, 2)
        if np.sum((np.sum(edge1, axis=-1) == 2)):
            # 这里是对边 对边是区分diff和 same的
            print("这里是对边")
            if style == "diff":
                img = remove_one_edge(img, imarray, edge[0]==1, False, edge[2]==1, False)
                imarray = np.array(img)
                img = remove_one_edge(img, imarray, False, edge[1] == 1, False, edge[3] == 1)
            elif style == "same":
                img = rm_edges(img, imarray, edge)
        elif edge is not None and np.sum((np.sum(edge, axis=-1) == 2)):
            #这里是临边 临边其实不区分
            print("这里是临边")
            img = rm_edges(img, imarray, edge)
    elif edge is not None and sum(edge) >= 2:
        img = rm_edges(img, imarray, edge)
    elif edge == None:
        img = remove_one_edge(img, imarray, True, False, True, False)
        imarray = np.array(img)
        img = remove_one_edge(img, imarray, False, True, False, True)

    return img
path = "E:\\docu\\QQ\\file\\frame000.png"
img = Image.open(path)
#imarray = np.array(img)
# type(imarray)  imarray.shape imarray.ndim
img = remove_edge(img, [1,0,1,0])
print(img.width, img.height)
img.show()