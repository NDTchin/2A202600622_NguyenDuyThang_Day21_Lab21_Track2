# Bao Cao Ngan Day21 Lab21 Track2

## 1. Mo hinh va cau hinh duoc chon
Trong qua trinh thu nghiem, em da so sanh nhieu cau hinh voi MLflow, bao gom `RandomForest`, `ExtraTrees`, `GradientBoosting`, `HistGradientBoosting`, `LogisticRegression` va cac mo hinh ensemble. Cau hinh cuoi cung duoc chon la mo hinh `VotingClassifier` ket hop giua `RandomForest` va `ExtraTrees` trong `scikit-learn`.

Cac tham so chinh duoc su dung:
- `model_type: voting_rf_et`
- `n_estimators: 800`
- `min_samples_split: 2`
- `voting: hard`
- `include_phase2_data: true`
- `phase2_data_path: data/train_phase2.csv`

Ly do lua chon cau hinh nay la vi tren tap danh gia `eval.csv`, day la cau hinh cho ket qua tot nhat trong nhom mo hinh `scikit-learn` ma em thu nghiem, dong thoi vuot nguong danh gia `accuracy >= 0.70` cua pipeline CI/CD.

## 2. Ket qua thu nghiem va ly do lua chon
O giai doan dau, khi chi huan luyen tren `train_phase1.csv`, nhieu cau hinh chi dat muc accuracy xap xi `0.68 - 0.69`, chua du de qua `eval gate`. Sau do em toi uu lai huong tiep can theo hai diem:
- dung ensemble manh hon trong `scikit-learn`
- huan luyen tren tap du lieu rong hon bang cach ket hop `train_phase1.csv` va `train_phase2.csv`

Ket qua tot nhat da xac nhan:
- `accuracy: 0.7700`
- `f1_score: 0.7686`

Voi ket qua nay, workflow GitHub Actions da co the di qua cac job `Unit Test`, `Train`, `Eval`, va `Deploy` thanh cong.

## 3. Kho khan gap phai va cach giai quyet
Trong qua trinh thuc hien, em gap ba nhom kho khan chinh.

Thu nhat, project GCP dang dung chinh sach chan tao `service-account key`, nen cach xac thuc bang file `sa-key.json` trong huong dan mac dinh khong con phu hop. Em da chuyen sang dung `Workload Identity Federation` cho GitHub Actions va gan truc tiep service account vao VM de truy cap GCS ma khong can key file.

Thu hai, model ban dau chua dat nguong `0.70`, nen job `Eval` trong pipeline bi chan dung nhu thiet ke. Em da toi uu mo hinh theo huong ensemble `RandomForest + ExtraTrees` va mo rong du lieu huan luyen bang `train_phase2.csv`, tu do nang accuracy len tren nguong yeu cau.

Thu ba, job `Deploy` tung that bai do service tren VM can them thoi gian de tai model tu GCS va khoi dong FastAPI. Em da cap nhat workflow de tang thoi gian cho va so lan retry health check, sau do deploy thanh cong.

## 4. Ket luan
Sau khi hoan thanh, he thong da dap ung day du quy trinh MLOps cua bai lab:
- theo doi thi nghiem bang MLflow
- quan ly du lieu bang DVC tren GCS
- huan luyen va danh gia tu dong bang GitHub Actions
- chi deploy khi mo hinh dat nguong chat luong
- phuc vu suy luan qua API tren VM cloud

Day la cau hinh cuoi cung em de xuat su dung cho bai nop.
