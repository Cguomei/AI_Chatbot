"""
意图识别模块 - AI 训练师的核心技能
教会机器人理解用户的真实意图
"""
from typing import List, Dict, Tuple
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle


class IntentClassifier:
    """意图分类器"""
    
    # 预定义的意图类型
    INTENT_TYPES = {
        "greeting": "打招呼",
        "shipping": "物流查询",
        "order_status": "订单状态",
        "return_refund": "退换货",
        "product_info": "商品信息",
        "payment": "支付问题",
        "invoice": "发票问题",
        "complaint": "投诉建议",
        "human_service": "转人工客服",
        "goodbye": "告别"
    }
    
    def __init__(self, model_path: str = "data/intent_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.training_data = []
        
    def prepare_training_data(self) -> Tuple[List[str], List[str]]:
        """
        准备训练数据
        返回：(文本列表，标签列表)
        """
        # 每个意图的训练样本（实际应用中应该更多）
        data = {
            "greeting": [
                "你好", "您好", "早上好", "下午好", "在吗", "有人吗",
                "你好啊", "哈喽", "hi", "hello", "客服在吗"
            ],
            "shipping": [
                "什么时候发货", "发货了吗", "物流信息", "快递到哪了",
                "怎么还没收到货", "配送需要多久", "包邮吗",
                "发货地在哪里", "用的什么快递", "能指定快递吗"
            ],
            "order_status": [
                "我的订单呢", "订单查询", "订单状态", "下单成功了吗",
                "订单号是多少", "查看订单", "订单详情",
                "为什么订单被取消了", "订单多久能到"
            ],
            "return_refund": [
                "我要退货", "怎么退款", "退换货流程", "可以换货吗",
                "退货地址", "退款多久到账", "运费谁出",
                "拆封了能退吗", "不支持无理由退换吗"
            ],
            "product_info": [
                "这个有货吗", "什么材质", "尺寸多大", "有哪些颜色",
                "保质期多久", "产地哪里", "适合什么人用",
                "是正品吗", "有优惠吗", "质量怎么样"
            ],
            "payment": [
                "怎么付款", "支持花呗吗", "可以用信用卡吗",
                "付款失败", "价格不对", "有优惠券吗",
                "能货到付款吗", "分期免息吗"
            ],
            "invoice": [
                "开发票", "电子发票", "发票怎么开", "发票抬头",
                "发票寄到哪里", "发票税点", "能补开发票吗"
            ],
            "complaint": [
                "我要投诉", "服务态度差", "商品有问题",
                "虚假宣传", "质量太差", "要举报你们"
            ],
            "human_service": [
                "转人工", "人工客服", "找真人", "不要机器人",
                "叫你们经理来", "跟活人说话"
            ],
            "goodbye": [
                "再见", "拜拜", "谢谢", "麻烦了",
                "好的知道了", "就这样吧", "先这样"
            ]
        }
        
        texts = []
        labels = []
        
        for intent, examples in data.items():
            texts.extend(examples)
            labels.extend([intent] * len(examples))
        
        return texts, labels
    
    def train(self, use_custom_data: bool = False):
        """
        训练意图识别模型
        
        Args:
            use_custom_data: 是否使用自定义数据（否则使用预置数据）
        """
        print("🎯 开始训练意图识别模型...")
        
        # 准备数据
        if use_custom_data and os.path.exists("data/custom_intent_data.json"):
            with open("data/custom_intent_data.json", 'r', encoding='utf-8') as f:
                custom_data = json.load(f)
            texts = custom_data.get("texts", [])
            labels = custom_data.get("labels", [])
        else:
            texts, labels = self.prepare_training_data()
        
        print(f"📚 训练数据：{len(texts)} 条样本")
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        # 构建 pipeline：TF-IDF + 朴素贝叶斯
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),  # 使用 unigram 和 bigram
                max_features=5000,
                min_df=1
            )),
            ('clf', MultinomialNB(alpha=0.5))  # 平滑参数
        ])
        
        # 训练模型
        self.model.fit(X_train, y_train)
        
        # 评估模型
        y_pred = self.model.predict(X_test)
        print("\n📊 模型评估报告:")
        print(classification_report(y_test, y_pred, 
                                   target_names=list(self.INTENT_TYPES.values())))
        
        # 保存模型
        self.save_model()
        print("✅ 模型训练完成！")
        
        return self.model
    
    def predict(self, text: str) -> Tuple[str, float, str]:
        """
        预测用户意图
        
        Args:
            text: 用户输入的文本
            
        Returns:
            (意图类型，置信度，意图中文名)
        """
        if self.model is None:
            self.load_model()
        
        prediction = self.model.predict([text])[0]
        proba = self.model.predict_proba([text])[0]
        
        # 获取置信度
        confidence = max(proba)
        
        # 获取中文名称
        intent_cn = self.INTENT_TYPES.get(prediction, prediction)
        
        return prediction, confidence, intent_cn
    
    def save_model(self):
        """保存模型到文件"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"💾 模型已保存到：{self.model_path}")
    
    def load_model(self):
        """从文件加载模型"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"📂 已加载模型：{self.model_path}")
        else:
            print("⚠️  模型不存在，请先训练模型")
            self.train()
    
    def add_training_sample(self, text: str, intent: str):
        """
        添加训练样本（在线学习）
        
        Args:
            text: 文本内容
            intent: 意图标签
        """
        self.training_data.append({"text": text, "intent": intent})
        
        # 每积累 10 个新样本就重新训练
        if len(self.training_data) >= 10:
            print("🔄 检测到足够的新样本，开始重新训练...")
            self.train_with_new_data()
    
    def train_with_new_data(self):
        """使用新数据重新训练"""
        # 加载原有训练数据
        texts, labels = self.prepare_training_data()
        
        # 添加新样本
        for sample in self.training_data:
            texts.append(sample["text"])
            labels.append(sample["intent"])
        
        # 保存更新后的数据
        os.makedirs("data", exist_ok=True)
        with open("data/custom_intent_data.json", 'w', encoding='utf-8') as f:
            json.dump({
                "texts": texts,
                "labels": labels
            }, f, ensure_ascii=False, indent=2)
        
        # 清空临时数据
        self.training_data = []
        
        # 重新训练
        self.train(use_custom_data=True)


# 使用示例
if __name__ == "__main__":
    classifier = IntentClassifier()
    
    # 训练模型
    classifier.train()
    
    # 测试
    test_cases = [
        "你好，在吗？",
        "我的订单怎么还没到？",
        "我想退货怎么办？",
        "这个是什么材质的？",
        "能开发票吗？",
        "转人工客服"
    ]
    
    print("\n" + "="*50)
    print("🧪 意图识别测试")
    print("="*50)
    
    for text in test_cases:
        intent, confidence, intent_cn = classifier.predict(text)
        print(f"\n输入：{text}")
        print(f"预测：{intent} ({intent_cn})")
        print(f"置信度：{confidence:.2%}")
