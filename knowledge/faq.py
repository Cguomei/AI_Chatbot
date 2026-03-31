"""
知识库管理模块
包含 FAQ 问答和商品信息
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class FAQManager:
    """FAQ 问答对管理"""
    
    def __init__(self, data_file: str = "data/faq.json"):
        self.data_file = data_file
        self.faqs = []
        self._load_faqs()
    
    def _load_faqs(self):
        """加载 FAQ 数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.faqs = json.load(f)
            print(f"📚 已加载 {len(self.faqs)} 条 FAQ")
        else:
            # 初始化默认 FAQ
            self.faqs = self._get_default_faqs()
            self._save_faqs()
    
    def _get_default_faqs(self) -> List[Dict]:
        """获取默认 FAQ 数据"""
        return [
            {
                "id": 1,
                "question": "什么时候发货？",
                "answer": "亲，我们一般在下单后 24 小时内发货，节假日顺延。发货后会通过短信通知您物流单号哦~",
                "keywords": ["发货", "配送", "快递", "什么时候发"],
                "category": "物流",
                "create_time": datetime.now().isoformat()
            },
            {
                "id": 2,
                "question": "支持七天无理由退换吗？",
                "answer": "是的，我们支持 7 天无理由退换货。商品需保持完好未使用状态，包装配件齐全。退回运费由买家承担哦~",
                "keywords": ["退换", "退货", "换货", "七天无理由"],
                "category": "售后",
                "create_time": datetime.now().isoformat()
            },
            {
                "id": 3,
                "question": "如何查询物流信息？",
                "answer": "您可以在'我的订单'页面点击'查看物流'按钮，或者告诉我您的订单号，我帮您查询~",
                "keywords": ["物流", "快递", "查询", "跟踪"],
                "category": "物流",
                "create_time": datetime.now().isoformat()
            },
            {
                "id": 4,
                "question": "可以开发票吗？",
                "answer": "可以的，我们提供电子发票。下单时填写发票抬头和税号，发票会在确认收货后 3 个工作日内开具并发送到您的邮箱。",
                "keywords": ["发票", "开票", "报销", "税票"],
                "category": "发票",
                "create_time": datetime.now().isoformat()
            },
            {
                "id": 5,
                "question": "用什么快递？",
                "answer": "我们默认使用中通、圆通、韵达等快递，具体以发货时为准。如有特殊要求可在订单备注，我们会尽量安排~",
                "keywords": ["快递", "物流", "中通", "圆通"],
                "category": "物流",
                "create_time": datetime.now().isoformat()
            },
            {
                "id": 6,
                "question": "多久能收到货？",
                "answer": "一般发货后 2-5 天送达，偏远地区可能需要 5-7 天。具体时效以快递公司为准哦~",
                "keywords": ["多久", "几天", "时效", "到达时间"],
                "category": "物流",
                "create_time": datetime.now().isoformat()
            },
            {
                "id": 7,
                "question": "怎么联系人工客服？",
                "answer": "您可以直接说'转人工'，我会为您转接人工客服。人工服务时间：9:00-22:00",
                "keywords": ["人工", "真人", "客服", "电话"],
                "category": "其他",
                "create_time": datetime.now().isoformat()
            },
            {
                "id": 8,
                "question": "支持花呗付款吗？",
                "answer": "支持的，我们支持花呗、信用卡、微信支付、支付宝等多种支付方式。部分商品还支持分期付款哦~",
                "keywords": ["花呗", "付款", "支付", "分期"],
                "category": "支付",
                "create_time": datetime.now().isoformat()
            }
        ]
    
    def _save_faqs(self):
        """保存 FAQ 数据"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.faqs, f, ensure_ascii=False, indent=2)
    
    def search_faq(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        搜索相关 FAQ
        
        Args:
            query: 用户问题
            top_k: 返回最匹配的 K 条结果
            
        Returns:
            相关 FAQ 列表
        """
        scores = []
        
        for faq in self.faqs:
            score = 0
            
            # 关键词匹配
            for keyword in faq.get("keywords", []):
                if keyword in query:
                    score += 2
            
            # 问题相似度（简单版本）
            query_words = set(query)
            question_words = set(faq["question"])
            overlap = len(query_words & question_words)
            score += overlap * 0.5
            
            if score > 0:
                scores.append((score, faq))
        
        # 按分数排序
        scores.sort(key=lambda x: x[0], reverse=True)
        
        return [faq for score, faq in scores[:top_k]]
    
    def add_faq(self, question: str, answer: str, keywords: List[str], category: str = "其他") -> int:
        """添加新的 FAQ"""
        faq_id = max([f["id"] for f in self.faqs], default=0) + 1
        
        new_faq = {
            "id": faq_id,
            "question": question,
            "answer": answer,
            "keywords": keywords,
            "category": category,
            "create_time": datetime.now().isoformat()
        }
        
        self.faqs.append(new_faq)
        self._save_faqs()
        
        print(f"✅ 已添加 FAQ #{faq_id}: {question}")
        return faq_id
    
    def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set()
        for faq in self.faqs:
            categories.add(faq.get("category", "其他"))
        return sorted(list(categories))


class ProductDatabase:
    """商品信息数据库（简化版）"""
    
    def __init__(self, data_file: str = "data/products.json"):
        self.data_file = data_file
        self.products = {}
        self._load_products()
    
    def _load_products(self):
        """加载商品数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.products = json.load(f)
            print(f"📦 已加载 {len(self.products)} 个商品")
        else:
            # 初始化示例商品
            self.products = self._get_sample_products()
            self._save_products()
    
    def _get_sample_products(self) -> Dict[str, Dict]:
        """获取示例商品数据"""
        return {
            "P001": {
                "name": "智能蓝牙耳机",
                "price": 199.00,
                "stock": 500,
                "description": "高清音质，降噪功能，续航 30 小时",
                "specs": {"颜色": ["黑色", "白色", "蓝色"], "版本": ["标准版", "Pro 版"]},
                "category": "数码配件"
            },
            "P002": {
                "name": "便携式充电宝 10000mAh",
                "price": 89.00,
                "stock": 1000,
                "description": "轻薄便携，双 USB 输出，快充技术",
                "specs": {"颜色": ["白色", "粉色"], "容量": ["10000mAh", "20000mAh"]},
                "category": "数码配件"
            },
            "P003": {
                "name": "纯棉四件套床上用品",
                "price": 299.00,
                "stock": 200,
                "description": "100% 纯棉，柔软舒适，环保印染",
                "specs": {"尺寸": ["1.5m 床", "1.8m 床"], "颜色": ["简约灰", "温馨粉", "天空蓝"]},
                "category": "家居家纺"
            }
        }
    
    def _save_products(self):
        """保存商品数据"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """根据 ID 查询商品"""
        return self.products.get(product_id)
    
    def search_products(self, keyword: str) -> List[Dict]:
        """搜索商品"""
        results = []
        keyword_lower = keyword.lower()
        
        for pid, product in self.products.items():
            # 搜索商品名称、描述、分类
            if (keyword_lower in product["name"].lower() or 
                keyword_lower in product["description"].lower() or
                keyword_lower in product["category"].lower()):
                results.append({
                    "id": pid,
                    **product
                })
        
        return results
    
    def check_stock(self, product_id: str) -> Dict:
        """查询商品库存"""
        product = self.products.get(product_id)
        if product:
            return {
                "product_id": product_id,
                "name": product["name"],
                "in_stock": product["stock"] > 0,
                "stock_quantity": product["stock"],
                "status": "有货" if product["stock"] > 0 else "缺货"
            }
        return {"error": "商品不存在"}


# 使用示例
if __name__ == "__main__":
    # 测试 FAQ
    faq_mgr = FAQManager()
    
    print("="*50)
    print("🧪 FAQ 搜索测试")
    print("="*50)
    
    queries = ["什么时候发货", "怎么退货", "开发票"]
    for query in queries:
        results = faq_mgr.search_faq(query)
        print(f"\n问题：{query}")
        for i, faq in enumerate(results, 1):
            print(f"{i}. {faq['question']}")
            print(f"   答案：{faq['answer'][:50]}...")
    
    # 测试商品
    print("\n" + "="*50)
    print("🧪 商品查询测试")
    print("="*50)
    
    prod_db = ProductDatabase()
    
    # 搜索商品
    results = prod_db.search_products("耳机")
    print(f"\n搜索'耳机'找到 {len(results)} 个商品:")
    for prod in results:
        print(f"- {prod['name']} ¥{prod['price']}")
    
    # 查询库存
    stock_info = prod_db.check_stock("P001")
    print(f"\n商品 P001 库存：{stock_info}")
