import math

def score(
    subject_num,
    predicate_num,
    object_num,
    attribute_num,
    adverbial_num,
    complement_num,
    others_num):

    cc=subject_num+predicate_num+object_num
    mc=attribute_num+adverbial_num+complement_num+others_num
    ratio = cc / (mc + 1)
    log_score = math.log2(1 + ratio)
    scale_factor = 5  # 通过实验确定的缩放因子
    return log_score * scale_factor


print(score(1,1,1,0,0,0,0))
print(score(1,1,1,2,2,2,2))


## <span style="background-color: #FFFF00">黄色背景</span>

## 红色 标记 句子的主要成分
## 蓝色 标记 通过实时核查的部分
## 这句话的的修饰含量（分数，红色的程度）
### 这是<font color='#FFFF00'>红色文字</font>。
## 这句话可能涉及的传播学技巧分数（项目，分数，蓝色的程度）
### 这是<font color='#FFFF00'>红色文字</font>。


