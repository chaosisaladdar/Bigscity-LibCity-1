from libcity.config import ConfigParser
from libcity.data import get_dataset
from libcity.utils import get_executor
from libcity.utils import get_model

# 加载配置文件
config = ConfigParser(task='traffic_state_pred', model='DSTGCN',
                      dataset='BEIJING_RISK', config_file=None,
                      other_args={'batch_size': 2})
# config = ConfigParser(task='traffic_state_pred', model='GSNet',
#                       dataset='CHICAGO_RISK', config_file=None,
#                       other_args={'batch_size': 1})
# 如果是交通流量\速度预测任务，请使用下面的加载配置文件语句
# config = ConfigParser(task='traffic_state_pred', model='TemplateTSP',
#       dataset='METR_LA', config_file=None, other_args={'batch_size': 2})
# 加载数据模块
# config['device'] = 'cpu'
dataset = get_dataset(config)
# 数据预处理，划分数据集
train_data, valid_data, test_data = dataset.get_data()
data_feature = dataset.get_data_feature()
# 抽取一个 batch 的数据进行模型测试
batch = train_data.__iter__().__next__()
# print(batch)
# 加载模型
model = get_model(config, data_feature)
self = model.to(config['device'])
# 模型预测
batch.to_tensor(config['device'])
# res = model.predict(batch)
# print(res)
loss = model.calculate_loss(batch)
print(loss)
# 请自行确认 res 的 shape 是否符合赛道的约束
# 如果要加载执行器的话
executor = get_executor(config, model, data_feature)
print(executor)
