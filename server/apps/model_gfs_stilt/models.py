from django.db import models
from django.core.validators import RegexValidator  # 导入验证器
from utils.model import BaseModel


name_validator = RegexValidator(
    regex=r'^[a-zA-Z]+$',
    message='只允许使用大小写英文字母',
    code='letters_only'
)

class ModelGFSStilt(BaseModel):
    """GFS-STILT模型"""
    name = models.CharField(max_length=100, verbose_name="模型名称", validators=[name_validator])
    # receptor = models.ManyToManyField("Receptor", verbose_name="受体", related_name="model_gfs_stilts")
    description = models.TextField(blank=True, null=True, verbose_name="描述信息")
    xres = models.FloatField(verbose_name="X方向分辨率", default=0.001)
    yres = models.FloatField(verbose_name="Y方向分辨率", default=0.001)
    n_cores = models.IntegerField(verbose_name="计算核心数", default=8)
    gfs_file_retention_days = models.IntegerField(verbose_name="GFS文件保留天数", default=365)

    class Meta:
        verbose_name = "GFS-STILT模型"
        verbose_name_plural = "GFS-STILT模型管理"
        db_table = "g_model_config"

    def __str__(self):
        return self.name
    
    
class Region(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="区域名称")
    xmn = models.FloatField(verbose_name="最小经度")
    xmx = models.FloatField(verbose_name="最大经度")
    ymn = models.FloatField(verbose_name="最小纬度")
    ymx = models.FloatField(verbose_name="最大纬度")
    geojson = models.TextField(verbose_name="区域边界 GeoJSON", null=True, blank=True)

    class Meta:
        verbose_name = "区域"
        verbose_name_plural = "区域管理"
        db_table = "g_region"

    def __str__(self):
        return self.name
    

class Receptor(BaseModel):
    """受体模型"""
    name = models.CharField(max_length=100, verbose_name="受体名称")
    latitude = models.FloatField(verbose_name="纬度")
    longitude = models.FloatField(verbose_name="经度")
    height = models.IntegerField(verbose_name="高度（米）")
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, blank=True, related_name="receptors", verbose_name="所属区域"
    )
    description = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        verbose_name = "受体"
        verbose_name_plural = "受体管理"
        db_table = "g_receptor"

    def __str__(self):
        return self.name
    

class PollutantSource(BaseModel):
    """污染源模型"""
    name = models.CharField(max_length=100, help_text="污染源名称")
    description = models.TextField(blank=True, null=True, help_text="描述信息")
    latitude = models.FloatField(verbose_name="纬度")
    longitude = models.FloatField(verbose_name="经度")
    source_type = models.CharField(max_length=50, help_text="污染源类型")
    emission_rate = models.FloatField(help_text="排放率")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "污染源"
        verbose_name_plural = "污染源管理"
        db_table = "g_pollutant_source"
