import numpy as np
import pandas as pd
from typing import Optional, List
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

DEFAULT_FEATURES = ["RSI", "DMA_S", "DMA_L", "DMA_CROSS_UP"]

def _flatten_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    flat = []
    for c in out.columns:
        if isinstance(c, tuple):
            parts = [str(p) for p in c if p not in (None, "", " ")]
            name = "_".join(parts) if parts else ""
        else:
            name = str(c)
        flat.append(name.strip("_"))
    out.columns = flat
    return out

#Function to handle close name variability
def _pick_close_col(cols: List[str], symbol: Optional[str]) -> Optional[str]:
    if symbol and f"CLOSE_{symbol}" in cols:
        return f"CLOSE_{symbol}"
    for c in cols:
        if c.startswith("CLOSE_"):
            return c
    if "CLOSE" in cols:
        return "CLOSE"
    if symbol and f"ADJ CLOSE_{symbol}" in cols:
        return f"ADJ CLOSE_{symbol}"
    if "ADJ_CLOSE" in cols:
        return "ADJ_CLOSE"
    if "ADJ CLOSE" in cols:
        return "ADJ CLOSE"
    return None

def prepare_ml_df(df: pd.DataFrame, symbol: Optional[str] = None) -> pd.DataFrame:
    out = df.copy()
    out = _flatten_cols(out)
    close = _pick_close_col(list(out.columns), symbol)
        
    # Calculate target using the identified close column
    out["TARGET_UP"] = (out[close].shift(-1) > out[close]).astype(int)
    return out

def train_simple_classifier(
    df: pd.DataFrame,
    features: List[str],
    model_type: str = "logistic",
    random_state: int = 42,
    symbol: Optional[str] = None,
):

    data = prepare_ml_df(df, symbol=symbol)

    use_feats = features if features else ["RSI", "DMA_S", "DMA_L", "DMA_CROSS_UP"]

    data = data.dropna(subset=use_feats + ["TARGET_UP"])


    X = np.array(data[use_feats].values)
    y = np.array(data["TARGET_UP"].values)

    # Time-series split
    tss = TimeSeriesSplit(n_splits=4)
    for tr, te in tss.split(X):
        train_idx, test_idx = tr, te
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    clf = DecisionTreeClassifier(random_state=random_state, max_depth=5) if model_type == "tree" else LogisticRegression(max_iter=1000)
    clf.fit(X_train, y_train)  
    acc = accuracy_score(y_test, clf.predict(X_test))
    return clf, acc, data.index[test_idx], clf.predict(X_test)
