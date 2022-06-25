# from transformers import AutoTokenizer, AutoModel
# import torch
import jieba
import macropodus
import hanlp

if __name__ == '__main__':
    # text = "2010年上映的电影中推荐3部在100到200分钟内的电影，最好是科幻片"
    # text = ["二零一零年上映的电影中推荐三部在一百到两百分钟以内的电影，最好是科幻片","时长在100分钟左右的电影","我想看不超过两个小时的电影"]
    # text = ["一两个小时","一到俩小时",]
    text = [
        '100分钟左右',
        '100分钟以上',
        '不超过两个小时',
        '不少于两个小时',
        '100到200分钟内',
        '一个小时到两个小时以内',
        '一两个小时以内',
        '一两个小时左右',
        '1个小时到2个小时之间',
        '九十分钟以内/之内',
        '209分钟上下',
        '一百到一百五十分钟之间',
        '103到104之间',
        '两个小时不到',
        '不能低于一个半小时',
        '俩小时以内',
        '2.5小时以内',
        '2.5个小时以内',
        '不低于一个小时',
        '不到两个小时',
        '七八十分钟',
        '一到两三个小时',
        '半个小时',
        '一个半到两个半小时',
        "一个半到俩个半小时",
        "一个小时到两个小时以内",
    ]
    text = ['我想看爱情电影']

    # text = "王丽坤主演的电影中评分较高的是哪几部"
    # text= "世界上评分较高的五部电影"
    # res_num2chi = macropodus.num2chi(text)
    # HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)  # 世界最大中文语料库
    # print(res_num2chi)
    for t in text:
        print(list(jieba.tokenize(t)))
        # print(list(macropodus.cut(t)))
        # j = HanLP([t])
        # print(j)
        # print("text:%s,tok:%s,pos:%s" % (t,j['tok/fine'],j['pos/pku'],))
