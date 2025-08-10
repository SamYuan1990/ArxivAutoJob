from deepSeekmodel import DeepSeekModel
from AnalysisAgent import AnalysisAgent
from AnalysisResult import write_results_to_markdown
from SummaryAgent import SummaryAgent
from spo_score import filter_high_spo_sentences

import re
import yaml
import logging
import os

logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)

logging.getLogger("strands").setLevel(logging.DEBUG)

model = DeepSeekModel(
    api_key=os.environ["api_key"],
    base_url="https://api.deepseek.com",
    model_id="deepseek-chat",
)

with open("config.yaml", "r", encoding="utf-8") as f:
     config = yaml.safe_load(f)

# Create an agent with tools from the strands-tools example tools package
# as well as our custom letter_counter tool
analysisAgent = AnalysisAgent(
    config=config,
    model=model
)

article = """
家庭暴力的世界现状
针对妇女的暴力行为是世界范围内的普遍现象：全球近 35%的妇女自 15 岁起就遭受过亲密伴侣或非伴侣的暴力行为（WHO， 2013）。
根据世界卫生组织 2018年发布的《全球、区域及国家针对妇女的家庭暴力发生率调查》，针对妇女的暴力行为被国际普遍认为是影响妇女生活和健康的一个严重和普遍的因素，是对妇女权利的严重侵犯。
调查显示， 针对妇女的暴力行为，一方面对妇女、 儿童和家庭的身心健康和福祉有短期、中期和长期影响：研究发现，在家暴环境长大的儿童可能具有表达能力较差（Huth-Bocks 等, 1999）， 智商较低（Koenen 等， 2003）的特征； 另一方面家庭暴力给国家和社会带来了严重的社会和经济后果：据估计，在美国，家暴带来的社会成本超过 58 亿美元 （Aizer， 2010）。
家暴带来的影响不仅体现在当代，研究表明，家暴具有代际遗传特征，在暴力家庭长大的人往往会将暴力行为遗传下去 （Pollak， 2004）。
因此如果没有外界干预， 短期内家暴并不会自行消失。近三十年来，世界各国都在呼吁消除和减少家庭暴力带来的伤害。
世界卫生组织 2018 年发布的《全球、区域及国家针对妇女的家庭暴力发生率调查》 中显示适龄女性的家庭暴力终身发生率仍然高达 27%， 即有 27%的女性一生中至少遭受过一次来自丈夫或男性亲密伴侣的身体和/或性暴力侵害，这意味着全球有 6.41-7.53 亿 15 岁以上的妇女遭受过家庭暴力。
值得强调的是， 所有调查都会低估针对妇女的暴力行为的真实发生率，因为总有妇女不会披露这些遭遇，因此家庭暴力的发生率要高于调查数据。
为了减少家暴的发生， 各国政府都出台了多类政策， 这些政策可以分为两类，第一类是通过提高女性的家庭内部议价权进而降低被家暴的概率。 
例如许多国家出台的《单边离婚法案》 ，该法案在不同程度上允许个体单方面提出离婚，使得受害者脱离家暴的成本降低，因此减少了家庭暴力的发生率。 
第二类政策致力于增加对家暴行为的惩处力度，例如部分国家和地区出台的《立即逮捕法案》 ，该法案规定无需受害者同意， 只要符合条件就可以逮捕家暴者，对于这一法案的效果，至今没有完全明晰。
家庭暴力的中印现状在中国，根据中国社会科学院的数据，近 30%的家庭成员遭受过不同程度的家庭暴力，其中 90%的施暴者为男性。
从时间来看，根据中国妇女社会地位调查：1990 年的调查数据显示我国妇女经历家庭暴力占比为 30%，2000 年的调查数据显示我国妇女经历家庭暴力占比为 22.5%，而在 2001 年随着《离婚法》的出台与宣传，2010 年的调查数据显示我国妇女遭受家庭暴力的占比降至 8.8%，2015年时我国又通过了《反家庭暴力法》 ，随着该法在 2016 年的开始实行，2020 年调查数据显示我国妇女遭受家暴的占比进一步下降。
整体来看， 我国妇女遭受家暴的占比在不断下降，但仍有将近十分之一的妇女受到家暴的影响。
此外，在当今中国社会，家庭暴力仍然被视为家庭内部矛盾，受虐者难以向外寻求社会支持，导致他们在反抗和妥协中徘徊。
根据陈洪磊与陈明静 （2022）对 3961 份家暴裁判文书的分析， 当前在对家暴行为的司法救济中，对于家庭暴力主体范围和行为的定义存在差异，导致在人身安全保护令法定签发条件方面存在疑难点。
此外， 司法惯性和释法论证的不足， 以及受害方在举证过程中面临的困难等问题也是针对家庭暴力司法适用中的挑战。
在印度，根据印度国家犯罪研究局的官方报告，2019 年针对妇女的 40.5 万犯罪案件中，其中有超过 30%是家庭暴力案件。 2021 年印度 NFHS-5 数据显示，在 18~49 岁的印度女性中，近三分之一的人遭受过家庭暴力， 32%的已婚女性曾遭受伴侣在身体、性或情感等方面的暴力，其中 27%的女性在调查的近一年时间内至少遭受过一种形式的暴力。

不完善的法律制度与复杂的举报流程是印度家庭暴力频发的外在原因。 
早在1983 年，印度刑法典修订的第 498A 条就规定如果丈夫或夫家亲属虐待妇女， 处以最高三年的监禁及相应罚款。
2005 年 6 月，印度通过首部《反家庭暴力法》。
但印度反家庭暴力的法律并没有根据社会的变化进行修改。 
同时， 复杂的举报证据与流程，加之缺乏严格执法， 使印度反家庭暴力法律制度有名无实、 形同虚设，很多案件不了了之。
截至 2020 年底，基于第 498A 的定罪率不到 20%，印度法院总共有 65.1 万起 498A 家庭暴力案件悬而未决。
"""

messages = re.split(r'[。！？\n]\s*', article.strip())
messages = [s.strip() for s in messages if s.strip()]
# Ask the agent a question that uses the available tools
analysis_results = analysisAgent.process_messages(messages)
print("------")
print(analysis_results)
print("------")
filtered_sentences = filter_high_spo_sentences(analysis_results)
print("------")
print(filtered_sentences)
print("------")
summary_agent = SummaryAgent(
    config=config,
    model=model
)
summary_result = summary_agent.summary(filtered_sentences)
print(summary_result)


write_results_to_markdown(str(summary_result),analysis_results,"./test12345.md")
