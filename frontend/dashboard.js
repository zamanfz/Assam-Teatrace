const API_BASE = "http://127.0.0.1:8000";

async function loadDashboard() {
    const gardenCount =
        document.getElementById("garden-count");

    const factoryCount =
        document.getElementById("factory-count");

    const blendCount =
        document.getElementById("blend-count");

    const packageCount =
        document.getElementById("package-count");

    const auditStatus =
        document.getElementById("audit-status");

    const complianceTotal =
        document.getElementById("compliance-total");

    const compliancePass =
        document.getElementById("compliance-pass");

    const complianceFail =
        document.getElementById("compliance-fail");

    const complianceNotEvaluated =
        document.getElementById("compliance-not-evaluated");

    try {
        const response = await fetch(
            `${API_BASE}/api/dashboard/summary`
        );

        if (!response.ok) {
            throw new Error(
                "Dashboard data unavailable"
            );
        }

        const data = await response.json();

        gardenCount.textContent =
            data.counts.gardens;

        factoryCount.textContent =
            data.counts.factory_batches;

        blendCount.textContent =
            data.counts.blend_batches;

        packageCount.textContent =
            data.counts.packages;

        if (data.audit.valid) {
            auditStatus.textContent = "✓ VALID";
            auditStatus.style.color = "#176b3a";
        } else {
            auditStatus.textContent = "✕ INVALID";
            auditStatus.style.color = "#a52b2b";
        }

        complianceTotal.textContent =
            data.compliance.total;

        compliancePass.textContent =
            `✓ ${data.compliance.pass}`;

        complianceFail.textContent =
            data.compliance.fail;

        complianceNotEvaluated.textContent =
            data.compliance.not_evaluated;

        if (data.compliance.fail > 0) {
            complianceFail.style.color = "#a52b2b";
            complianceFail.style.fontWeight = "700";
        } else {
            complianceFail.style.color = "#176b3a";
        }

    } catch (error) {

        console.error(
            "TeaTrace dashboard error:",
            error
        );

        gardenCount.textContent = "—";
        factoryCount.textContent = "—";
        blendCount.textContent = "—";
        packageCount.textContent = "—";

        complianceTotal.textContent = "—";
        compliancePass.textContent = "—";
        complianceFail.textContent = "—";
        complianceNotEvaluated.textContent = "—";

        auditStatus.textContent =
            "UNAVAILABLE";

        auditStatus.style.color =
            "#a52b2b";
    }
}

loadDashboard();