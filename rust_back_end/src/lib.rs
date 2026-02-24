use pyo3::prelude::*;

#[pyfunction]
fn backend_version() -> &'static str {
    "0.1.0"
}

#[pymodule]
fn rust_back_end(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(backend_version, m)?)?;
    Ok(())
}
