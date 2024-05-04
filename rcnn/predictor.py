import os
from django.utils import timezone
from django.conf import settings
from core.models import Images, System, Detections
from datetime import datetime
import time as timer
import torch
from celery import shared_task
from io import BytesIO
import numpy as np
from django.core.files.base import ContentFile
import time

# Singleton class
class RCNNPredictor:
    def __new__(cls,*args, **kwargs):
        if not hasattr(cls, 'instance') and torch.cuda.is_available():
            import detectron2
            from tensorflow.keras.models import load_model
            from detectron2.engine import DefaultTrainer
            from detectron2.config import get_cfg
            from detectron2 import model_zoo
            from detectron2.engine import DefaultPredictor
            
            from detectron2.data.datasets import register_coco_instances
            from detectron2.data import MetadataCatalog
            
            import pandas as pd
            
            
            import boto3

            TORCH_VERSION = ".".join(torch.__version__.split(".")[:2])
            CUDA_VERSION = torch.__version__.split("+")[-1]
            print("torch: ", TORCH_VERSION, "; cuda: ", CUDA_VERSION)
            print("detectron2:", detectron2.__version__)

            cls.instance = super(RCNNPredictor, cls).__new__(cls,*args, **kwargs)
            cfg = get_cfg()
            cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
            cfg.DATASETS.TRAIN = ("training_dataset",)
            cfg.DATASETS.TEST = ()
            cfg.DATALOADER.NUM_WORKERS = 2
            cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_50_FPN_3x")  # Let training initialize from model zoo
            cfg.SOLVER.IMS_PER_BATCH = 2  # This is the real "batch size" commonly known to deep learning people
            cfg.SOLVER.BASE_LR = 0.00025  # pick a good LR
            cfg.SOLVER.MAX_ITER = 300    # 300 iterations seems good enough for this toy dataset; you will need to train longer for a practical dataset
            cfg.SOLVER.STEPS = []        # do not decay learning rate
            cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128   # The "RoIHead batch size". 128 is faster, and good enough for this toy dataset (default: 512)
            cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # only has one class (ballon). (see https://detectron2.readthedocs.io/tutorials/datasets.html#update-the-config-for-new-datasets)
            cfg.MODEL.WEIGHTS = os.path.join("rcnn/rcnn_model.pth")  # path to the model we just trained
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7   # set a custom testing threshold

            # Force CPU inference for GCP Engine
            cfg.MODEL.DEVICE = 'cpu'

            register_coco_instances("training_dataset", {}, "data/json_annotation_train.json", "data/train")
            cls.instance.metadata = MetadataCatalog.get('training_dataset')

            cls.instance.cfg = cfg
            cls.instance.predictor = DefaultPredictor(cfg)
            cls.instance.tracker = {}

            cls.instance.s3 = boto3.client('s3', 
                                    region_name=settings.AWS_S3_REGION_NAME,
                                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                                )
        elif not torch.cuda.is_available():
            print("CUDA not available")
            cls.instance = super(RCNNPredictor, cls).__new__(cls,*args, **kwargs)
        else:
            print("Instance already exists")
        return cls.instance
    
    def __init__(self) -> None:
        if not torch.cuda.is_available():
            raise Exception("Model requires CUDA to run. Please run on a machine with CUDA support.")
        
    def _get_tracker(self, system_id):
        from .sort import Sort
        if system_id not in self.tracker:
            tracker = Sort()
            detections = Detections.objects.filter(system_id=system_id).values_list('x1','y1','x2','y2','score')
            detections_np = np.array([np.array(detection) for detection in detections])
            tracker.update(detections_np)
            self.tracker[system_id] = tracker
        return self.tracker[system_id]
    
    def predict(self, file_name, system_id):
        from PIL import Image
        from detectron2.utils.visualizer import Visualizer, ColorMode
    
        import cv2
        

        time = timer.time()
        # print(self)
        file = self.s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_name)
        file_content = file['Body'].read()
        img = Image.open(BytesIO(file_content))
        img = np.array(img)
        
        print(f"Prediction time: {timer.time() - time}")
        

        print(f"Prediction time: {timer.time() - time}")
        outputs = self.predictor(img)
        print(f"Prediction time: {timer.time() - time}")
        v = Visualizer(img[:, :, ::-1],
                   metadata= self.metadata,
                   scale=0.5,
                   instance_mode=ColorMode.IMAGE   # remove the colors of unsegmented pixels. This option is only available for segmentation models
        )
        print(f"Prediction time: {timer.time() - time}")
        out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
        
        print(f"Prediction time: {timer.time() - time}")
        
        boxes = outputs["instances"].pred_boxes.tensor.cpu().numpy()
        scores = outputs["instances"].scores.cpu().numpy()
        # classes = outputs["instances"].pred_classes.cpu().numpy()
        formatted_boxes = np.column_stack((boxes, scores))
        trackers = self._get_tracker(system_id).update(formatted_boxes)

        print(f"Prediction time: {timer.time() - time}")

        id_list = Detections.objects.filter(system_id=system_id).values_list('id',flat=True)

        print(f"Prediction time: {timer.time() - time}")

        new_detection_count = 0
        detections = []
        for i, result in enumerate(trackers):
            x1, y1, x2, y2, id = result
            if id not in id_list:
                detections += {
                    'detection_id': id,
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'score': scores[i],
                    'detected_time': timezone.now()
                }
                new_detection_count+=1
                
                # if created:
                #     print("Created new detection")

        print(f"Prediction time: {timer.time() - time}")

        self.s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_name)

        _, buffer = cv2.imencode('.jpg', out.get_image()[:, :, ::-1])
  

        return ( file_name,
                    detections,
                    new_detection_count, 
                    buffer)
 

@shared_task(bind=True)
def predict(self, file_name, system: System) -> np.ndarray:
    start_time = time.time()

    predictor = RCNNPredictor()
    file_name, detections, new_detection_count, image = predictor.predict(file_name,system.id)

    for d in detections:
            Detections.objects.update_or_create(detection_id=id,system= d['detection_id'], defaults={
                    'x1': d['x1'],
                    'y1': d['y1'],
                    'x2': d['x2'],
                    'y2': d['y2'],
                    'score': d['scores'],
                    'detected_time': d['detected_time'],
            })

    Images.objects.create(**{
        "photo": ContentFile(image,f'system_{system.id}_{datetime.now().isoformat()}.jpg'),
        "prediction_time" : time.time() - start_time,
        "system": system,
        "area": system.coverage,
        "detected_mosquito_count": new_detection_count
    })

    return
