from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import JsonResponse, HttpResponse
import pendulum
from loguru import logger
from celery import current_app
from utils import utils_netcdf
from .models import Region, Receptor, ModelGFSStilt, PollutantSource
from .serializers import RegionSerializer, ReceptorSerializer, ModelGFSStiltSerializer, PollutantSourceSerializer
from .tasks import run_gfs_stilt_task


class ModelGFSStiltViewSet(viewsets.ModelViewSet):
    queryset = ModelGFSStilt.objects.all()
    serializer_class = ModelGFSStiltSerializer
    permission_classes = []
    authentication_classes = []

    @action(detail=False, methods=['get'])
    def create_task(self, request):
        run_date = request.query_params.get('run_date')
        receptor_ids = request.query_params.get('receptor_ids')
        inspect = current_app.control.inspect()
        worker_dict = inspect.active()
        queue_length = -1
        for worker_name, task_list in worker_dict.items():
            if "gfs_stilt_worker" in worker_name:
                queue_length = len(task_list)
        if queue_length > 10:
            return JsonResponse({"error": f"任务队列已满,请稍后再试,任务数:{queue_length}"}, status=400)
        if not run_date:
            run_date = pendulum.now().subtract(days=1).format("YYYY-MM-DD")
        if not receptor_ids:
            receptor_ids = ""
        run_gfs_stilt_task.delay(run_date, receptor_ids)
        return JsonResponse({"message": "任务已经创建,请等待完成"})

    
    @action(detail=False, methods=['get'])
    def get_stilt_data(self, request):
        """
        获取某一受体 STILT 模型的数据
        """
        try:
            time = request.query_params.get('time')
            receptor_id = request.query_params.get('receptor_id')
            resp_type = request.query_params.get('resp_type')
            if not all([time, receptor_id]):
                return JsonResponse({"error": "缺少必要参数,请提供time,receptor_id"}, status=400) 
            if receptor_id:
                receptor = Receptor.objects.get(id=receptor_id)
                lng = receptor.longitude
                lat = receptor.latitude
                height = receptor.height
            height = int(height)
            file = utils_netcdf.parse_file_name(time=time, lng=lng, lat=lat, hight=height)
            data = utils_netcdf.get_nc_data(file)
            lng = [row[0] for row in data["data"]]
            lat = [row[1] for row in data["data"]]
            data['bounds'] = [[min(lat), min(lng)], [max(lat), max(lng)]]

            if resp_type == 'png':
                buffer = utils_netcdf.stilt_to_png(data)
                return HttpResponse(buffer.getvalue(), content_type='image/png')
            else:
                return JsonResponse(data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def get_stilt_merge_data(self, request):
        """
        获取某一受体 STILT 多时段合并数据
        """
        st = request.query_params.get('st')
        et = request.query_params.get('et')
        receptor_id = request.query_params.get('receptor_id')
        resp_type = request.query_params.get('resp_type')
        if not all([st, et, receptor_id]):
                return JsonResponse({"error": "缺少必要参数,请提供st, et, receptor_id"}, status=400) 
        st = pendulum.from_format(st, 'YYYYMMDDHHmm')
        et = pendulum.from_format(et, 'YYYYMMDDHHmm')
        
        if receptor_id:
            receptor = Receptor.objects.get(id=receptor_id)
            lng = receptor.longitude
            lat = receptor.latitude
            height = int(receptor.height)

        all_data = []
        all_data_dict = {}
        columns = []
        not_exist_files = []
        while st <= et:
            tm_str = st.format('YYYYMMDDHHmm')[:-2] + '00'
            try:
                file = utils_netcdf.parse_file_name(time=tm_str, lng=lng, lat=lat, hight=height)
                data = utils_netcdf.get_nc_data(file)
                value_data = data['data']
                columns = data['columns']
                for i in value_data:
                    grid_key = f"{i[0]}:{i[1]}"
                    all_data_dict.setdefault(grid_key, []).append(i[2])
                st = st.add(hours=1)
            except Exception as e:
                logger.error(e)
                not_exist_files.append(tm_str)
                st = st.add(hours=1)
                continue

        for k in all_data_dict:
            [lng, lat] = k.split(':')
            avg_val = sum(all_data_dict[k]) / len(all_data_dict[k])
            all_data.append([float(lng), float(lat), avg_val])
        data = {"columns": columns, "data": all_data}
        lng = [row[0] for row in data["data"]]
        lat = [row[1] for row in data["data"]]
        data['bounds'] = [[min(lat), min(lng)], [max(lat), max(lng)]]

        if resp_type == 'png':
            buffer = utils_netcdf.stilt_to_png(data)
            return HttpResponse(buffer.getvalue(), content_type='image/png')
        else:
            return JsonResponse(data)


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class ReceptorViewSet(viewsets.ModelViewSet):
    queryset = Receptor.objects.filter(is_deleted=False)
    serializer_class = ReceptorSerializer
    permission_classes = []
    authentication_classes = []


class PollutantSourceViewSet(viewsets.ModelViewSet):
    queryset = PollutantSource.objects.all()
    serializer_class = PollutantSourceSerializer
    permission_classes = []
    authentication_classes = []