'''
SET SQL_SAFE_UPDATES = 0;

UPDATE Models
SET website_url = 'https://aihub.qualcomm.com/models/detr_resnet101?domain=Computer+Vision&useCase=Object+Detection', article_url = 'https://paperswithcode.com/paper/end-to-end-object-detection-with-transformers'
WHERE model_name = 'DETR-ResNet101';

UPDATE Models
SET website_url = 'https://aihub.qualcomm.com/models/detr_resnet101_dc5?domain=Computer+Vision&useCase=Object+Detection', article_url = 'https://paperswithcode.com/paper/end-to-end-object-detection-with-transformers'
WHERE model_name = 'DETR-ResNet101-DC5';

UPDATE Models
SET website_url = 'https://aihub.qualcomm.com/models/detr_resnet50?domain=Computer+Vision&useCase=Object+Detection', article_url = 'https://paperswithcode.com/paper/end-to-end-object-detection-with-transformers'
WHERE model_name = 'DETR-ResNet50';

UPDATE Models
SET website_url = 'https://aihub.qualcomm.com/models/detr_resnet50_dc5?domain=Computer+Vision&useCase=Object+Detection', article_url = 'https://paperswithcode.com/paper/end-to-end-object-detection-with-transformers'
WHERE model_name = 'DETR-ResNet50-DC5';

SET SQL_SAFE_UPDATES = 1;
'''