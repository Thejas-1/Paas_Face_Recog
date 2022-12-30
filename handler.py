import boto3
import face_recognition
import pickle
from botocore.exceptions import ClientError
import os

output_bucket = "cloudguru-outputbucket"
dynamodb_table_name = 'paas-project'

s3 = boto3.client('s3', aws_access_key_id='AKIAQEQYM2VWQAQ3Z6IB', aws_secret_access_key='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', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', aws_access_key_id='AKIAQEQYM2VWQAQ3Z6IB', aws_secret_access_key='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', region_name='us-east-1')


def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def face_recognition_handler(event, context):

	bucket_name = event['Records'][0]['s3']['bucket']['name']
	s3_key = event['Records'][0]['s3']['object']['key']

	folder_path = '/tmp/'
	video_location = str(folder_path) + s3_key

	frame_location = f'{folder_path}frames/'
	if not os.path.exists(frame_location):
		os.mkdir(frame_location)

	try:
		s3.download_file(bucket_name, s3_key, video_location)
	except ClientError as exp:
		if exp.response['Error']['Code'] == '404':
			print(f'The file is not present in bucket://{bucket_name}/{s3_key}')
			return
		else: raise exp

	os.system("ffmpeg -i " + str(video_location) + " -r 1 " + str(frame_location) + "image-%3d.jpeg")

	list_of_frames = sorted(os.listdir(frame_location))
	for frme in list_of_frames:
		imge = face_recognition.load_image_file(os.path.join(frame_location, frme))
		list_of_face_encodings = face_recognition.face_encodings(imge)
		if len(list_of_face_encodings) > 0:
			face_detected = list_of_face_encodings[0]
			break

	encoding_location = '/home/app/encoding'
	all_available_face_lists = open_encoding(encoding_location)

	final_result = face_recognition.compare_faces(all_available_face_lists['encoding'], face_detected)
	ind = final_result.index(True)
	detected_face = list(all_available_face_lists['name'])[ind]

	std_tble = dynamodb.Table(dynamodb_table_name)
	face_detected_info = std_tble.get_item(Key={'name': detected_face})['Item']
	csv_file = f"{face_detected_info['name']},{face_detected_info['major']},{face_detected_info['year']}"

	s3.put_object(Bucket=output_bucket, Key=s3_key.replace(".mp4", ".csv"), Body=csv_file)
	return csv_file