import pulumi
import pulumi_aws as aws

# define the environment for the bucket
env = 'prod'


# create the S3 bucket
bucket_tw = aws.s3.Bucket(f"s3-bucket-tech-week-2-awsome-{env}",
    acl="private",
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
    website=aws.s3.BucketWebsiteArgs(
        index_document=f"{env}.html",
        error_document="error.html"
    ))

s3_origin_id = f"s3-bucket-tech-week-2-awsome-{env}"


# create the CloudFront distribution
distribution = aws.cloudfront.Distribution("s3Distribution",
    origins=[aws.cloudfront.DistributionOriginArgs(
        domain_name=bucket_tw.bucket_regional_domain_name,
        origin_access_control_id=aws_cloudfront_origin_access_control["default"]["id"],
        origin_id=s3_origin_id,
        s3_origin_config=aws.cloudfront.DistributionOriginS3OriginConfigArgs(
        origin_access_identity=aws_cloudfront_origin_access_identity["example"]["cloudfront_access_identity_path"],
    )
    )],
    enabled=True,
    comment="Some comment",
    default_root_object= f"{env}.html",
    default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
        allowed_methods=[
            "GET",
            "HEAD",
        ],
        target_origin_id=s3_origin_id,
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


# Create a bucket policy to allow CloudFront to read objects from the bucket
s3_policy = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
    actions=["s3:GetObject"],
    resources=[f"{bucket_tw['example']['arn']}/*"],
    principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
        type="AWS",
        identifiers=[aws_cloudfront_origin_access_identity["example"]["iam_arn"]],
    )],
)])


bucket_policy = aws.s3.BucketPolicy("example",
    bucket=bucket_tw["example"]["id"],
    policy=s3_policy.json)
