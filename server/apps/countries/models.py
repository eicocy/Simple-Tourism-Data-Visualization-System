"""国家模块数据模型。"""

from django.db import models


class Country(models.Model):
    """国家基础信息表。"""

    # 国家中文名称，用于系统展示
    name_zh = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="国家中文名",
        help_text="国家的中文名称，例如日本、法国。",
    )
    # 国家英文名称，用于国际化和数据导入匹配
    name_en = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="国家英文名",
        help_text="国家的英文名称，例如 Japan、France。",
    )
    # 国家代码，便于后续对接标准数据源
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="国家代码",
        help_text="国家简写代码，例如 JP、FR。",
    )
    # 所属洲别，用于筛选和统计
    continent = models.CharField(
        max_length=50,
        verbose_name="所属洲",
        help_text="国家所属大洲，例如亚洲、欧洲。",
    )
    # 首都信息
    capital = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="首都",
        help_text="国家首都名称，可为空。",
    )
    # 官方语言
    language = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="官方语言",
        help_text="国家官方语言，可为空。",
    )
    # 货币信息
    currency = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="货币",
        help_text="国家主要货币名称，可为空。",
    )
    # 是否在系统中启用显示
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用",
        help_text="表示该国家数据是否在系统中启用展示。",
    )
    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        help_text="当前记录的创建时间。",
    )
    # 更新时间
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间",
        help_text="当前记录的最后更新时间。",
    )

    class Meta:
        db_table = "country"
        verbose_name = "国家信息"
        verbose_name_plural = "国家信息"
        ordering = ["name_zh"]

    def __str__(self):
        """返回国家名称。"""
        return self.name_zh


class CountryIndicator(models.Model):
    """国家指标表。"""

    # 关联国家表，一国可对应多条年度指标数据
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="indicators",
        verbose_name="所属国家",
        help_text="指标所属的国家。",
    )
    # 数据所属年份
    year = models.PositiveIntegerField(
        verbose_name="年份",
        help_text="该条指标数据对应的年份。",
    )
    # 安全指数，数值越高表示越安全
    safety_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="安全指数",
        help_text="国家整体安全水平评分，建议 0 到 100。",
    )
    # 消费指数，当前由人均 GDP 标准化后得到，数值越高表示消费压力越高
    cost_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="消费指数",
        help_text="国家旅游消费水平评分，建议 0 到 100。",
    )
    # 旅游适宜指数，用于区分典型旅游目的地与非旅游型国家
    tourism_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50,
        verbose_name="旅游适宜指数",
        help_text="反映国家旅游资源、接待能力和目的地吸引力的综合评分，建议 0 到 100。",
    )
    # 气候舒适度
    climate_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="气候指数",
        help_text="国家气候舒适度评分，建议 0 到 100。",
    )
    # 医疗保障指数
    medical_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="医疗指数",
        help_text="国家医疗保障水平评分，建议 0 到 100。",
    )
    # 签证便利度
    visa_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="签证便利指数",
        help_text="国家签证便利程度评分，建议 0 到 100。",
    )
    # 综合评分，当前项目中主要用于存储幸福指数数据
    overall_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="综合评分",
        help_text="当前项目中用于存储幸福指数或综合评分结果。",
    )
    # 数据来源说明
    data_source = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="数据来源",
        help_text="指标数据来源说明，可为空。",
    )
    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        help_text="当前记录的创建时间。",
    )
    # 更新时间
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间",
        help_text="当前记录的最后更新时间。",
    )

    class Meta:
        db_table = "country_indicator"
        verbose_name = "国家指标"
        verbose_name_plural = "国家指标"
        unique_together = ("country", "year")
        ordering = ["-year", "-overall_score"]

    def __str__(self):
        """返回国家年度指标的简要信息。"""
        return f"{self.country.name_zh}-{self.year}"
