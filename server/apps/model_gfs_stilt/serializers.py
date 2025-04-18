from rest_framework import serializers
from .models import Region, Receptor, ModelGFSStilt, PollutantSource


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


class SimpleRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'xmn', 'xmx', 'ymn', 'ymx'] 


class ReceptorSerializer(serializers.ModelSerializer):
    region = SimpleRegionSerializer(read_only=True)
    class Meta:
        model = Receptor
        fields = "__all__"


class PollutantSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollutantSource
        fields = "__all__"


class ModelGFSStiltSerializer(serializers.ModelSerializer):
    receptor = ReceptorSerializer(many=True, read_only=True)

    class Meta:
        model = ModelGFSStilt
        fields = "__all__"