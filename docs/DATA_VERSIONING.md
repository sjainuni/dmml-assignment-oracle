# RecoMart – Data Versioning and Lineage

## 1. Overview

RecoMart implements data versioning using DVC (Data Version Control)
and data lineage tracking using SHA-256 manifests.

The implementation separates:
- Source code and version metadata in GitHub.
- Versioned dataset objects in OCI Object Storage.
- Local working copies and DVC cache in the Linux environment.

## 2. Dataset Versioning

DVC version: 3.67.1

The following Retailrocket source datasets are tracked:

| Dataset | Approximate Size |
|---|---:|
| events.csv | 90 MB |
| category_tree.csv | 15 KB |
| item_properties_part1.csv | 462 MB |
| item_properties_part2.csv | 390 MB |

DVC tracking directory:

    data/dvc_raw/

DVC metadata file:

    data/dvc_raw.dvc

The DVC directory metadata records:
- Directory checksum: 19cdee87944c59fc15c51396fe37cd88.dir
- Total size: 987,498,023 bytes
- Number of files: 4

DVC uses content hashes to identify dataset objects and
detect changes between versions.

## 3. Remote Storage Configuration

The DVC remote uses OCI Object Storage through its
S3-compatible API.

| Property | Configuration |
|---|---|
| Remote name | oci-dvc |
| Bucket | recomart-dmml-data |
| Prefix | dvc-store |
| Region | ap-mumbai-1 |
| Protocol | HTTPS |
| Authentication | OCI Customer Secret Key |
| S3 addressing | Path style |

Credentials are stored locally in:

    ~/.aws/credentials

They are not committed to GitHub.

## 4. GitHub and OCI Responsibilities

GitHub stores:
- Application source code.
- DVC metadata files.
- DVC remote configuration.
- Documentation and reports.

OCI Object Storage stores:
- DVC-managed dataset objects.
- Raw and processed pipeline artifacts.
- Feature and report artifacts.

The large CSV datasets and DVC cache are excluded from
normal Git tracking.

## 5. Data Lineage

The custom lineage implementation is located in:

    src/versioning.py

The snapshot function records:
- Dataset and artifact paths.
- File sizes in bytes.
- SHA-256 checksums.
- UTC snapshot creation timestamp.
- Source dataset information.
- Documented transformation steps.

Generated lineage metadata:

    reports/lineage_manifest.json

This provides a record of the files and transformations
used during pipeline execution.

Note: DVC's default content checksum is MD5, while the
custom lineage manifest uses SHA-256. They serve different
purposes in this implementation.

## 6. Dataset Versioning Workflow

### Track datasets

    dvc add data/dvc_raw

### Check local dataset status

    dvc status

### Upload dataset objects to OCI

    dvc push

### Check remote synchronization

    dvc status -c

### Restore datasets

    dvc pull

### Commit updated DVC metadata

    git add data/dvc_raw.dvc data/.gitignore
    git commit -m "Update dataset version"
    git push origin main

## 7. Reproducibility Verification

The following verification was completed:

1. DVC initialized successfully.
2. Four source CSV datasets were tracked.
3. DVC uploaded five objects to the OCI remote.
4. Remote synchronization returned:

       Cache and remote 'oci-dvc' are in sync.

5. A separate clean Git clone was created.
6. DVC pull successfully restored the four datasets.
7. The restored dataset directory was verified.

This demonstrates that dataset artifacts can be recovered
using GitHub metadata and OCI Object Storage.

## 8. Security

- OCI Customer Secret Keys are stored outside the project.
- AWS-compatible credentials are kept in ~/.aws/credentials.
- Credential files have restricted local permissions.
- No access keys or secret keys are stored in Git.
- The OCI bucket is private.

## 9. Conclusion

The project combines DVC-based dataset versioning,
OCI remote object storage and SHA-256 lineage manifests.

GitHub maintains the version metadata and source code,
while OCI stores the versioned dataset objects.

The successful upload, remote synchronization and
clean-clone restoration demonstrate the implemented
data versioning and reproducibility workflow.
