const API_BASE = "http://127.0.0.1:8000";


async function loadTraceExplorer() {

    const input = document.getElementById("package-code");
    const result = document.getElementById("trace-result");

    const qrCode = input.value.trim();


    if (!qrCode) {

        result.innerHTML = `
            <div class="trace-error">
                Please enter a QR/package code.
            </div>
        `;

        return;
    }


    result.innerHTML = `
        <div class="trace-card">

            <span class="trace-section-label">
                VERIFYING
            </span>

            <h2 class="trace-section-title">
                Reading provenance records...
            </h2>

            <p style="color:#748078;font-size:12px;">
                Connecting package, batch and compliance records.
            </p>

        </div>
    `;


    try {

        const response = await fetch(
            `${API_BASE}/api/public/trace/${encodeURIComponent(qrCode)}`
        );


        if (!response.ok) {
            throw new Error("Package trace not found");
        }


        const data = await response.json();

        renderTrace(data);

    } catch (error) {

        console.error(
            "Trace Explorer error:",
            error
        );


        result.innerHTML = `

            <div class="trace-error">

                <strong>
                    Trace unavailable
                </strong>

                <div style="margin-top:5px;">
                    ${error.message}
                </div>

            </div>

        `;
    }
}



function renderTrace(data) {

    const result =
        document.getElementById("trace-result");


    const firstSource =
        data.sources?.[0];


    if (!firstSource) {

        result.innerHTML = `
            <div class="trace-error">
                No provenance source information found.
            </div>
        `;

        return;
    }



    /* ==========================================
       FLOW
    ========================================== */

    let flowHTML = `

        <div class="trace-node">

            <div class="trace-node-icon">
                🌿
            </div>

            <strong>
                Tea Garden
            </strong>

            <small>
                ${firstSource.garden.name}
            </small>

        </div>


        <div class="trace-arrow">
            →
        </div>


        <div class="trace-node">

            <div class="trace-node-icon">
                🍃
            </div>

            <strong>
                Green Leaf
            </strong>

            <small>
                ${firstSource.green_leaf.lot_code}
            </small>

        </div>


        <div class="trace-arrow">
            →
        </div>


        <div class="trace-node">

            <div class="trace-node-icon">
                🏭
            </div>

            <strong>
                Factory
            </strong>

            <small>
                ${firstSource.factory.batch_code}
            </small>

        </div>


        <div class="trace-arrow">
            →
        </div>


        <div class="trace-node">

            <div class="trace-node-icon">
                🏬
            </div>

            <strong>
                Warehouse
            </strong>

            <small>
                ${firstSource.warehouse.name}
            </small>

        </div>

    `;


    data.sources.forEach(
        source => {

            flowHTML += `

                <div class="trace-arrow">
                    →
                </div>

                <div class="trace-node">

                    <div class="trace-node-icon">
                        🔨
                    </div>

                    <strong>
                        Auction
                    </strong>

                    <small>
                        ${source.auction_lot.code}
                    </small>

                </div>

            `;
        }
    );


    flowHTML += `

        <div class="trace-arrow">
            →
        </div>


        <div class="trace-node">

            <div class="trace-node-icon">
                🫖
            </div>

            <strong>
                Blend
            </strong>

            <small>
                ${data.blend.blend_code}
            </small>

        </div>


        <div class="trace-arrow">
            →
        </div>


        <div class="trace-node">

            <div class="trace-node-icon">
                📦
            </div>

            <strong>
                Package
            </strong>

            <small>
                ${data.package.package_code}
            </small>

        </div>

    `;



    /* ==========================================
       AUCTION SOURCES
    ========================================== */

    let sourceHTML = "";


    data.sources.forEach(
        (source, index) => {

            sourceHTML += `

                <div class="trace-source">

                    <span
                        class="trace-section-label"
                        style="margin-bottom:5px;"
                    >
                        SOURCE ${String(index + 1).padStart(2, "0")}
                    </span>

                    <h4>
                        🔨 ${source.auction_lot.code}
                    </h4>


                    <p>
                        <strong>
                            Auction Centre:
                        </strong>

                        ${source.auction_lot.auction_center}
                    </p>


                    <p>
                        <strong>
                            Grade:
                        </strong>

                        ${source.auction_lot.grade || "N/A"}
                    </p>


                    <p>
                        <strong>
                            Quantity:
                        </strong>

                        ${source.auction_lot.quantity_kg} kg
                    </p>


                    <p>
                        <strong>
                            Warehouse:
                        </strong>

                        ${source.warehouse.name || "N/A"}
                    </p>

                </div>

            `;
        }
    );



    /* ==========================================
       COMPLIANCE
    ========================================== */

    let complianceHTML = "";


    if (data.compliance) {

        const status =
            data.compliance.overall_status;


        const statusSymbol =
            status === "PASS"
                ? "✓"
                : status === "FAIL"
                    ? "✕"
                    : "•";


        const statusClass =
            status === "PASS"
                ? "pass"
                : status === "FAIL"
                    ? "fail"
                    : "unknown";


        const tests =
            data.compliance.tests || [];


        const testHTML =
            tests.map(
                test => {

                    const testStatus =
                        (test.result_status || "UNKNOWN")
                        .toLowerCase()
                        .replaceAll("_", "-");


                    let statusText =
                        test.result_status || "UNKNOWN";


                    let statusColor =
                        test.result_status === "PASS"
                            ? "#4d9167"
                            : test.result_status === "FAIL"
                                ? "#b64c4c"
                                : "#b08a4b";


                    return `

                        <div
                            class="trace-compliance-item ${testStatus}"
                        >

                            <strong>
                                ${test.parameter_name}
                            </strong>


                            <span
                                style="
                                    color:${statusColor};
                                "
                            >
                                ${statusText}
                            </span>


                            ${
                                test.maximum_allowed !== null
                                ?
                                `
                                <p
                                    style="
                                        margin-top:10px;
                                        color:#748078;
                                        font-size:10px;
                                    "
                                >
                                    Applicable limit:
                                    <strong>
                                        ${test.maximum_allowed}
                                        ${test.unit}
                                    </strong>
                                </p>
                                `
                                :
                                ""
                            }


                            ${
                                test.rule_source
                                ?
                                `
                                <p
                                    style="
                                        margin-top:5px;
                                        color:#748078;
                                        font-size:10px;
                                    "
                                >
                                    Rule source:
                                    ${test.rule_source}
                                </p>
                                `
                                :
                                ""
                            }

                        </div>

                    `;
                }
            ).join("");


        complianceHTML = `

            <div class="trace-card">

                <span class="trace-section-label">
                    05 / FOOD SAFETY
                </span>


                <h2 class="trace-section-title">
                    Compliance verification
                </h2>


                <div
                    class="trace-status"
                    style="
                        margin-bottom:25px;
                    "
                >

                    <span
                        style="
                            font-size:17px;
                        "
                    >
                        ${statusSymbol}
                    </span>

                    Overall status:
                    ${status}

                </div>


                <div class="trace-compliance-grid">

                    ${testHTML}

                </div>

            </div>

        `;
    }



    /* ==========================================
       MAIN OUTPUT
    ========================================== */

    result.innerHTML = `


        <!-- TRACE HEADER -->

        <div class="trace-card">

            <div
                style="
                    display:flex;
                    align-items:center;
                    justify-content:space-between;
                    gap:20px;
                    margin-bottom:25px;
                "
            >

                <div>

                    <span class="trace-section-label">
                        02 / VERIFIED PROVENANCE
                    </span>

                    <h2
                        class="trace-section-title"
                        style="margin-bottom:8px;"
                    >
                        ${data.package.brand_name}
                    </h2>

                    <p
                        style="
                            color:#748078;
                            font-size:12px;
                        "
                    >
                        Package

                        <strong
                            style="color:#12382b;"
                        >
                            ${data.package.package_code}
                        </strong>
                    </p>

                </div>


                <div
                    style="
                        padding:10px 14px;
                        border-radius:999px;
                        background:#e5eee4;
                        color:#3f7957;
                        font-size:10px;
                        font-weight:700;
                        white-space:nowrap;
                    "
                >
                    ✓ TRACEABLE
                </div>

            </div>


            <span class="trace-section-label">
                PROVENANCE CHAIN
            </span>


            <div class="trace-flow-wrapper">

                <div class="trace-flow">

                    ${flowHTML}

                </div>

            </div>

        </div>



        <!-- PRODUCT -->

        <div class="trace-card">

            <span class="trace-section-label">
                03 / PRODUCT
            </span>

            <h2 class="trace-section-title">
                Package details
            </h2>


            <div class="trace-details">


                <div class="trace-detail">

                    <span class="trace-detail-label">
                        Package
                    </span>

                    <span class="trace-detail-value">
                        ${data.package.package_code}
                    </span>

                </div>


                <div class="trace-detail">

                    <span class="trace-detail-label">
                        Brand
                    </span>

                    <span class="trace-detail-value">
                        ${data.package.brand_name}
                    </span>

                </div>


                <div class="trace-detail">

                    <span class="trace-detail-label">
                        Quantity
                    </span>

                    <span class="trace-detail-value">
                        ${data.package.quantity_kg} kg
                    </span>

                </div>


                <div class="trace-detail">

                    <span class="trace-detail-label">
                        Pack Size
                    </span>

                    <span class="trace-detail-value">
                        ${data.package.pack_size_kg} kg
                    </span>

                </div>


                <div class="trace-detail">

                    <span class="trace-detail-label">
                        Number of Packs
                    </span>

                    <span class="trace-detail-value">
                        ${data.package.number_of_packages}
                    </span>

                </div>


                <div class="trace-detail">

                    <span class="trace-detail-label">
                        Tea Type
                    </span>

                    <span class="trace-detail-value">
                        ${data.blend.tea_type}
                    </span>

                </div>


            </div>

        </div>



        <!-- ORIGIN -->

        <div class="trace-card">

            <span class="trace-section-label">
                04 / ORIGIN
            </span>

            <h2 class="trace-section-title">
                ${firstSource.garden.name}
            </h2>


            <div class="trace-details">


                <div class="trace-detail">

                    <span class="trace-detail-label">
                        Garden Code
                    </span>

                    <span class="trace-detail-value">
                        ${firstSource.garden.garden_code}
                    </span>

                </div>


                <div class="trace-detail">

                    <span class="trace-detail-label">
                        District
                    </span>

                    <span class="trace-detail-value">
                        ${firstSource.garden.district}
                    </span>

                </div>


                <div class="trace-detail">

                    <span class="trace-detail-label">
                        State
                    </span>

                    <span class="trace-detail-value">
                        ${firstSource.garden.state}
                    </span>

                </div>


                <div class="trace-detail">

                    <span class="trace-detail-label">
                        Harvest Lot
                    </span>

                    <span class="trace-detail-value">
                        ${firstSource.green_leaf.lot_code}
                    </span>

                </div>


            </div>

        </div>



        <!-- SOURCES -->

        <div class="trace-card">

            <span class="trace-section-label">
                05 / MARKET MOVEMENT
            </span>

            <h2 class="trace-section-title">
                Auction sources
            </h2>


            <p
                style="
                    color:#748078;
                    font-size:12px;
                    margin-bottom:20px;
                "
            >
                Recorded auction lots contributing to the
                downstream provenance chain.
            </p>


            ${sourceHTML}

        </div>


        <!-- COMPLIANCE -->

        ${complianceHTML}


        <!-- FINAL TRUST -->

        <div
            class="trace-card"
            style="
                background:#12382b;
                color:white;
                border:none;
            "
        >

            <div
                style="
                    display:flex;
                    align-items:center;
                    justify-content:space-between;
                    gap:25px;
                "
            >

                <div>

                    <span
                        style="
                            display:block;
                            color:#d2b47a;
                            font-size:9px;
                            font-weight:700;
                            letter-spacing:.18em;
                        "
                    >
                        ASSAM TEATRACE
                    </span>

                    <h2
                        style="
                            font-family:'Playfair Display',serif;
                            font-size:32px;
                            line-height:1;
                            margin-top:8px;
                        "
                    >
                        A trace you can follow.
                    </h2>

                    <p
                        style="
                            color:rgba(255,255,255,.58);
                            font-size:11px;
                            max-width:560px;
                            margin-top:12px;
                        "
                    >
                        Supply-chain records connect the
                        package to its recorded origin,
                        processing and market journey.
                    </p>

                </div>


                <a
                    href="index.html?code=${encodeURIComponent(
                        data.package.package_code
                    )}"
                    style="
                        display:inline-flex;
                        align-items:center;
                        padding:13px 18px;
                        background:#b08a4b;
                        color:white;
                        border-radius:999px;
                        font-size:10px;
                        font-weight:700;
                        white-space:nowrap;
                    "
                >
                    Consumer View →
                </a>

            </div>

        </div>

    `;
}


loadTraceExplorer();