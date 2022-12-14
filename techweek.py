import pulumi
import pulumi_aws as aws

# define the AWS region to deploy the resources
reg = pulumi.get_config("Reg")
# define the environment for the bucket
env = pulumi.get_config("Env")

# create the CloudFront origin identity
origin_identity = aws.cloudfront.CloudFrontOriginAccessIdentity(
    "CloudFrontOriginIdentity",
    cloudfront_origin_access_identity_config={
        "comment": "origin identity"
    }
)

# create the CloudFront distribution
distribution = aws.cloudfront.Distribution("cloudfront",
    origins=[aws.cloudfront.DistributionOriginArgs(
        domain_name=bucket.bucket_regional_domain_name,
        origin_access_control_id=aws_cloudfront_origin_access_control["default"]["id"],
        origin_id=bucket.id,
    )],
    enabled=True,
    comment="Some comment",
    default_root_object= f"{env}.html",
    default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
        allowed_methods=[
            "GET",
            "HEAD",
        ],
        target_origin_id=bucket.s3_origin_id,
        forwarded_values=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
            query_string=False,
            cookies=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                forward="none",
            ),
        ),
        viewer_protocol_policy="redirect-to-https",
    ),
    viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
        cloudfront_default_certificate=True,
    )    
)

# create the S3 bucket
bucket = aws.s3.Bucket(
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
bucket_policy = aws.s3.BucketPolicy(
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
