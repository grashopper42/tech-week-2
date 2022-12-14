import pulumi
from pulumi_aws import s3, cloudfront

# define the AWS region to deploy the resources
reg = pulumi.get_config("Reg")
# define the environment for the bucket
env = pulumi.get_config("Env")

# create the CloudFront origin identity
origin_identity = cloudfront.CloudFrontOriginAccessIdentity(
    "CloudFrontOriginIdentity",
    cloudfront_origin_access_identity_config={
        "comment": "origin identity"
    }
)

# create the CloudFront distribution
distribution = cloudfront.Distribution(
    "cloudfront",
    distribution_config={
        "enabled": True,
        "comment": "Some comment",
        "default_root_object": f"{env}.html",
        "origins": [
            {
                "domain_name": bucket.bucket_regional_domain_name,
                "id": bucket.id,
                "s3_origin_config": {
                    "origin_access_identity": origin_identity.cloudfront_access_identity_path
                }
            }
        ],
        "default_cache_behavior": {
            "allowed_methods": ["GET", "HEAD"],
            "target_origin_id":


# create the S3 bucket
bucket = s3.Bucket(
    "bucket",
    bucket=f"s3-bucket-tech-week-2-awsome-{env}",
    versioning={
        "status": "Enabled"
    },
    website={
        "index_document": f"{env}.html"
    }
)

# Create a bucket policy to allow CloudFront to read objects from the bucket
bucket_policy = s3.BucketPolicy(
    "BucketPolicy",
    bucket=bucket.id,
    policy=pulumi.interpolate(
        '''
        {{
            "Id": "1",
            "Version": "2012-10-17",
            "Statement": [
                {{
                    "Action": "s3:GetObject",
                    "Effect": "Allow",
                    "Principal": {{
                        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity ${cloudfront_origin_identity}"
                    }},
                    "Resource": "arn:aws:s3:::{bucket_name}/*"
                }}
            ]
        }}
        ''',
        cloudfront_origin_identity=pulumi.get_stack(),
        bucket_name=bucket.bucket_name,
    ),
)
