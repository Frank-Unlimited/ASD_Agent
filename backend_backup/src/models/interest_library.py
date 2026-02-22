"""
标准兴趣点库
定义 ASD 儿童常见的兴趣点分类和标准化名称
"""
from typing import Dict, List
from pydantic import BaseModel, Field
from .profile import InterestCategory


class StandardInterest(BaseModel):
    """标准化兴趣点"""
    interest_key: str = Field(..., description="唯一标识")
    name: str = Field(..., description="显示名称")
    category: InterestCategory = Field(..., description="类别")
    description: str = Field(default="", description="描述")
    related_materials: List[str] = Field(default_factory=list, description="相关材料")
    keywords: List[str] = Field(default_factory=list, description="关键词（用于匹配）")


# 标准兴趣点库
STANDARD_INTERESTS: Dict[str, StandardInterest] = {
    # ========== 视觉类 ==========
    "visual_colorful_blocks": StandardInterest(
        interest_key="visual_colorful_blocks",
        name="彩色积木",
        category=InterestCategory.VISUAL,
        description="对彩色积木、拼图等视觉刺激强的玩具感兴趣",
        related_materials=["乐高", "木质积木", "彩色拼图"],
        keywords=["积木", "彩色", "拼图", "颜色"]
    ),
    "visual_spinning_objects": StandardInterest(
        interest_key="visual_spinning_objects",
        name="旋转物体",
        category=InterestCategory.VISUAL,
        description="喜欢观察旋转的物体",
        related_materials=["旋转齿轮", "陀螺", "风车", "转盘"],
        keywords=["旋转", "转动", "齿轮", "陀螺", "风车"]
    ),
    "visual_light_shadow": StandardInterest(
        interest_key="visual_light_shadow",
        name="光影玩具",
        category=InterestCategory.VISUAL,
        description="对光影、反射、投影等视觉效果感兴趣",
        related_materials=["手电筒", "投影仪", "镜子", "棱镜"],
        keywords=["光", "影子", "反射", "投影", "镜子"]
    ),
    "visual_picture_books": StandardInterest(
        interest_key="visual_picture_books",
        name="绘本",
        category=InterestCategory.VISUAL,
        description="喜欢看图画书、绘本",
        related_materials=["图画书", "绘本", "卡片书"],
        keywords=["绘本", "图画书", "书", "图片"]
    ),
    "visual_gears": StandardInterest(
        interest_key="visual_gears",
        name="旋转齿轮",
        category=InterestCategory.VISUAL,
        description="对齿轮、机械结构感兴趣",
        related_materials=["齿轮玩具", "机械积木"],
        keywords=["齿轮", "机械", "转动"]
    ),
    "visual_patterns": StandardInterest(
        interest_key="visual_patterns",
        name="条纹图案",
        category=InterestCategory.VISUAL,
        description="喜欢观察条纹、图案",
        related_materials=["条纹卡片", "图案书"],
        keywords=["条纹", "图案", "纹理"]
    ),
    "visual_animation": StandardInterest(
        interest_key="visual_animation",
        name="动画片段",
        category=InterestCategory.VISUAL,
        description="喜欢看动画、视频",
        related_materials=["平板电脑", "电视"],
        keywords=["动画", "视频", "动画片", "卡通"]
    ),
    
    # ========== 听觉类 ==========
    "auditory_songs": StandardInterest(
        interest_key="auditory_songs",
        name="儿歌",
        category=InterestCategory.AUDITORY,
        description="喜欢听儿歌、童谣",
        related_materials=["音乐播放器", "儿歌书"],
        keywords=["儿歌", "童谣", "歌曲", "音乐"]
    ),
    "auditory_instruments": StandardInterest(
        interest_key="auditory_instruments",
        name="乐器声",
        category=InterestCategory.AUDITORY,
        description="对乐器声音感兴趣",
        related_materials=["小鼓", "铃铛", "木琴", "沙锤"],
        keywords=["乐器", "鼓", "铃铛", "木琴"]
    ),
    "auditory_nature": StandardInterest(
        interest_key="auditory_nature",
        name="自然音",
        category=InterestCategory.AUDITORY,
        description="喜欢听自然声音（水声、鸟叫等）",
        related_materials=["自然音效播放器"],
        keywords=["水声", "鸟叫", "风声", "自然"]
    ),
    "auditory_mechanical": StandardInterest(
        interest_key="auditory_mechanical",
        name="机械声",
        category=InterestCategory.AUDITORY,
        description="对机械声音感兴趣（马达、齿轮等）",
        related_materials=["电动玩具", "机械玩具"],
        keywords=["机械", "马达", "引擎", "齿轮声"]
    ),
    "auditory_audio_books": StandardInterest(
        interest_key="auditory_audio_books",
        name="有声书",
        category=InterestCategory.AUDITORY,
        description="喜欢听有声书、故事",
        related_materials=["有声书", "故事机"],
        keywords=["有声书", "故事", "朗读"]
    ),
    "auditory_rhythm": StandardInterest(
        interest_key="auditory_rhythm",
        name="节奏打击乐",
        category=InterestCategory.AUDITORY,
        description="喜欢有节奏的声音和打击乐",
        related_materials=["鼓", "沙锤", "响板"],
        keywords=["节奏", "打击乐", "鼓点"]
    ),
    "auditory_voice_stories": StandardInterest(
        interest_key="auditory_voice_stories",
        name="人声故事",
        category=InterestCategory.AUDITORY,
        description="喜欢听人讲故事",
        related_materials=["故事书", "录音"],
        keywords=["故事", "讲述", "人声"]
    ),
    
    # ========== 触觉类 ==========
    "tactile_clay": StandardInterest(
        interest_key="tactile_clay",
        name="黏土",
        category=InterestCategory.TACTILE,
        description="喜欢玩黏土、橡皮泥",
        related_materials=["黏土", "橡皮泥", "超轻黏土"],
        keywords=["黏土", "橡皮泥", "泥巴"]
    ),
    "tactile_sand": StandardInterest(
        interest_key="tactile_sand",
        name="沙子",
        category=InterestCategory.TACTILE,
        description="喜欢玩沙子、沙盘",
        related_materials=["沙盘", "动力沙", "沙滩玩具"],
        keywords=["沙子", "沙盘", "沙滩"]
    ),
    "tactile_water": StandardInterest(
        interest_key="tactile_water",
        name="水",
        category=InterestCategory.TACTILE,
        description="喜欢玩水、水流",
        related_materials=["水杯", "水盆", "水枪"],
        keywords=["水", "水流", "倒水", "玩水"]
    ),
    "tactile_soft_gel": StandardInterest(
        interest_key="tactile_soft_gel",
        name="软胶玩具",
        category=InterestCategory.TACTILE,
        description="喜欢软胶、硅胶材质的玩具",
        related_materials=["软胶球", "硅胶玩具"],
        keywords=["软胶", "硅胶", "软"]
    ),
    "tactile_plush": StandardInterest(
        interest_key="tactile_plush",
        name="毛绒材质",
        category=InterestCategory.TACTILE,
        description="喜欢毛绒玩具、柔软材质",
        related_materials=["毛绒玩具", "绒布"],
        keywords=["毛绒", "柔软", "绒布"]
    ),
    "tactile_smooth_blocks": StandardInterest(
        interest_key="tactile_smooth_blocks",
        name="光滑积木",
        category=InterestCategory.TACTILE,
        description="喜欢光滑表面的积木",
        related_materials=["木质积木", "塑料积木"],
        keywords=["光滑", "积木", "木质"]
    ),
    "tactile_texture_cards": StandardInterest(
        interest_key="tactile_texture_cards",
        name="纹理卡片",
        category=InterestCategory.TACTILE,
        description="喜欢触摸不同纹理的卡片",
        related_materials=["纹理卡片", "触觉书"],
        keywords=["纹理", "触觉", "卡片"]
    ),
    
    # ========== 运动类 ==========
    "motor_slide": StandardInterest(
        interest_key="motor_slide",
        name="滑梯",
        category=InterestCategory.MOTOR,
        description="喜欢玩滑梯",
        related_materials=["滑梯"],
        keywords=["滑梯", "滑"]
    ),
    "motor_swing": StandardInterest(
        interest_key="motor_swing",
        name="秋千",
        category=InterestCategory.MOTOR,
        description="喜欢荡秋千",
        related_materials=["秋千"],
        keywords=["秋千", "荡"]
    ),
    "motor_trampoline": StandardInterest(
        interest_key="motor_trampoline",
        name="蹦床",
        category=InterestCategory.MOTOR,
        description="喜欢跳蹦床",
        related_materials=["蹦床"],
        keywords=["蹦床", "跳"]
    ),
    "motor_cycling": StandardInterest(
        interest_key="motor_cycling",
        name="骑车",
        category=InterestCategory.MOTOR,
        description="喜欢骑车、滑板车",
        related_materials=["自行车", "滑板车", "平衡车"],
        keywords=["骑车", "自行车", "滑板车"]
    ),
    "motor_ball_games": StandardInterest(
        interest_key="motor_ball_games",
        name="抛接球",
        category=InterestCategory.MOTOR,
        description="喜欢玩球类游戏",
        related_materials=["球", "篮球", "足球"],
        keywords=["球", "抛", "接", "踢"]
    ),
    "motor_spinning": StandardInterest(
        interest_key="motor_spinning",
        name="转圈游戏",
        category=InterestCategory.MOTOR,
        description="喜欢转圈、旋转",
        related_materials=["转椅", "旋转盘"],
        keywords=["转圈", "旋转", "转"]
    ),
    "motor_balance_beam": StandardInterest(
        interest_key="motor_balance_beam",
        name="感统平衡木",
        category=InterestCategory.MOTOR,
        description="喜欢平衡类活动",
        related_materials=["平衡木", "平衡板"],
        keywords=["平衡", "平衡木", "走"]
    ),
    
    # ========== 建构类 ==========
    "construction_lego": StandardInterest(
        interest_key="construction_lego",
        name="乐高",
        category=InterestCategory.CONSTRUCTION,
        description="喜欢玩乐高积木",
        related_materials=["乐高", "得宝"],
        keywords=["乐高", "LEGO", "积木"]
    ),
    "construction_magnetic": StandardInterest(
        interest_key="construction_magnetic",
        name="磁力片",
        category=InterestCategory.CONSTRUCTION,
        description="喜欢玩磁力片",
        related_materials=["磁力片", "磁力积木"],
        keywords=["磁力片", "磁铁", "磁力"]
    ),
    "construction_blocks": StandardInterest(
        interest_key="construction_blocks",
        name="积木",
        category=InterestCategory.CONSTRUCTION,
        description="喜欢搭建积木",
        related_materials=["木质积木", "塑料积木"],
        keywords=["积木", "搭建", "建构"]
    ),
    "construction_assembly": StandardInterest(
        interest_key="construction_assembly",
        name="拆装玩具",
        category=InterestCategory.CONSTRUCTION,
        description="喜欢拆装、组装玩具",
        related_materials=["螺丝玩具", "组装车"],
        keywords=["拆", "装", "组装", "螺丝"]
    ),
    "construction_origami": StandardInterest(
        interest_key="construction_origami",
        name="折纸",
        category=InterestCategory.CONSTRUCTION,
        description="喜欢折纸",
        related_materials=["彩纸", "折纸书"],
        keywords=["折纸", "纸", "折"]
    ),
    "construction_craft": StandardInterest(
        interest_key="construction_craft",
        name="手工材料",
        category=InterestCategory.CONSTRUCTION,
        description="喜欢手工制作",
        related_materials=["彩纸", "胶水", "剪刀", "贴纸"],
        keywords=["手工", "制作", "DIY"]
    ),
    "construction_gears": StandardInterest(
        interest_key="construction_gears",
        name="齿轮组",
        category=InterestCategory.CONSTRUCTION,
        description="喜欢组装齿轮玩具",
        related_materials=["齿轮积木", "机械组"],
        keywords=["齿轮", "机械", "组装"]
    ),
    
    # ========== 秩序类 ==========
    "order_sorting": StandardInterest(
        interest_key="order_sorting",
        name="排序玩具",
        category=InterestCategory.ORDER,
        description="喜欢排序、排列",
        related_materials=["排序板", "数字卡片"],
        keywords=["排序", "排列", "顺序"]
    ),
    "order_classification": StandardInterest(
        interest_key="order_classification",
        name="分类盒",
        category=InterestCategory.ORDER,
        description="喜欢分类、归类",
        related_materials=["分类盒", "颜色分类"],
        keywords=["分类", "归类", "整理"]
    ),
    "order_stacking": StandardInterest(
        interest_key="order_stacking",
        name="叠叠乐",
        category=InterestCategory.ORDER,
        description="喜欢叠高、堆叠",
        related_materials=["叠叠乐", "套杯"],
        keywords=["叠", "堆", "叠高"]
    ),
    "order_arrangement": StandardInterest(
        interest_key="order_arrangement",
        name="物品摆放游戏",
        category=InterestCategory.ORDER,
        description="喜欢摆放、整理物品",
        related_materials=["收纳盒", "玩具架"],
        keywords=["摆放", "整理", "收纳"]
    ),
    "order_sequence_cards": StandardInterest(
        interest_key="order_sequence_cards",
        name="流程卡片",
        category=InterestCategory.ORDER,
        description="喜欢按流程排列卡片",
        related_materials=["流程卡", "故事卡"],
        keywords=["流程", "顺序", "步骤"]
    ),
    
    # ========== 认知类 ==========
    "cognitive_numbers": StandardInterest(
        interest_key="cognitive_numbers",
        name="数字卡片",
        category=InterestCategory.COGNITIVE,
        description="对数字感兴趣",
        related_materials=["数字卡片", "数字书"],
        keywords=["数字", "数", "计数"]
    ),
    "cognitive_letters": StandardInterest(
        interest_key="cognitive_letters",
        name="字母书",
        category=InterestCategory.COGNITIVE,
        description="对字母、文字感兴趣",
        related_materials=["字母卡", "识字书"],
        keywords=["字母", "文字", "识字"]
    ),
    "cognitive_maps": StandardInterest(
        interest_key="cognitive_maps",
        name="地图",
        category=InterestCategory.COGNITIVE,
        description="喜欢看地图、地球仪",
        related_materials=["地图", "地球仪"],
        keywords=["地图", "地球仪", "地理"]
    ),
    "cognitive_car_logos": StandardInterest(
        interest_key="cognitive_car_logos",
        name="车标图",
        category=InterestCategory.COGNITIVE,
        description="对车标、标志感兴趣",
        related_materials=["车标卡片", "汽车书"],
        keywords=["车标", "标志", "汽车"]
    ),
    "cognitive_animals": StandardInterest(
        interest_key="cognitive_animals",
        name="动物模型",
        category=InterestCategory.COGNITIVE,
        description="喜欢动物模型、动物书",
        related_materials=["动物模型", "动物图鉴"],
        keywords=["动物", "模型", "图鉴"]
    ),
    "cognitive_experiments": StandardInterest(
        interest_key="cognitive_experiments",
        name="实验玩具",
        category=InterestCategory.COGNITIVE,
        description="喜欢科学实验、探索",
        related_materials=["科学实验盒", "显微镜"],
        keywords=["实验", "科学", "探索"]
    ),
    
    # ========== 社交类 ==========
    "social_turn_taking": StandardInterest(
        interest_key="social_turn_taking",
        name="回合制游戏",
        category=InterestCategory.SOCIAL,
        description="喜欢回合制游戏（传球、躲猫猫等）",
        related_materials=["球", "玩具"],
        keywords=["传球", "躲猫猫", "轮流", "回合"]
    ),
    "social_role_play": StandardInterest(
        interest_key="social_role_play",
        name="角色扮演玩具",
        category=InterestCategory.SOCIAL,
        description="喜欢角色扮演游戏",
        related_materials=["厨房玩具", "医生玩具", "娃娃"],
        keywords=["角色", "扮演", "过家家"]
    ),
    "social_interactive_books": StandardInterest(
        interest_key="social_interactive_books",
        name="互动绘本",
        category=InterestCategory.SOCIAL,
        description="喜欢需要互动的绘本",
        related_materials=["翻翻书", "触摸书"],
        keywords=["互动", "绘本", "翻翻书"]
    ),
}


def get_interest_by_key(interest_key: str) -> StandardInterest:
    """根据键获取标准兴趣点"""
    return STANDARD_INTERESTS.get(interest_key)


def get_interests_by_category(category: InterestCategory) -> List[StandardInterest]:
    """根据类别获取标准兴趣点列表"""
    return [
        interest for interest in STANDARD_INTERESTS.values()
        if interest.category == category
    ]


def search_interests(keyword: str) -> List[StandardInterest]:
    """根据关键词搜索标准兴趣点"""
    keyword_lower = keyword.lower()
    results = []
    for interest in STANDARD_INTERESTS.values():
        if (keyword_lower in interest.name.lower() or
            keyword_lower in interest.description.lower() or
            any(keyword_lower in kw.lower() for kw in interest.keywords)):
            results.append(interest)
    return results


def get_all_categories() -> List[InterestCategory]:
    """获取所有兴趣类别"""
    return list(InterestCategory)


__all__ = [
    'StandardInterest',
    'STANDARD_INTERESTS',
    'get_interest_by_key',
    'get_interests_by_category',
    'search_interests',
    'get_all_categories'
]
