const params = new URLSearchParams(window.location.search);
const qrCode = params.get("code") || "TEA-PKG-0001";

async function loadTrace() {
    const status = document.getElementById("status");
    const packageSection = document.getElementById("package");
    const originSection = document.getElementById("origin");
    const journeySection = document.getElementById("journey");
    const complianceSection = document.getElementById("compliance");

    try {
        const response = await fetch(
            `http://127.0.0.1:8000/api/public/trace/${qrCode}`
        );

        if (!response.ok) {
            throw new Error("Trace information not found");
        }

        const data = await response.json();

        status.innerHTML = `
            <h2 class="success">✓ Verified Traceability</h2>
            <p>Authentic provenance information is available for this package.</p>
            <p><strong>${data.package.package_code}</strong></p>
        `;

        packageSection.innerHTML = `
            <div class="section-heading">
                <div>
                    <span class="eyebrow">PRODUCT IDENTITY</span>
                    <h2>${data.package.brand_name}</h2>
                </div>
                <span class="section-icon">▣</span>
            </div>

            <div class="package-grid">

                <div class="info-box">
                    <div class="info-label">Package Code</div>
                    <div class="info-value">
                        ${data.package.package_code}
                    </div>
                </div>

                <div class="info-box">
                    <div class="info-label">Pack Size</div>
                    <div class="info-value">
                        ${data.package.pack_size_kg} kg
                    </div>
                </div>

                <div class="info-box">
                    <div class="info-label">Total Quantity</div>
                    <div class="info-value">
                        ${data.package.quantity_kg} kg
                    </div>
                </div>

                <div class="info-box">
                    <div class="info-label">Number of Packs</div>
                    <div class="info-value">
                        ${data.package.number_of_packages}
                    </div>
                </div>

            </div>
        `;

        const firstSource = data.sources[0];

        if (firstSource) {

            originSection.innerHTML = `
                <div class="section-heading">
                    <div>
                        <span class="eyebrow">ORIGIN</span>
                        <h2>${firstSource.garden.name}</h2>
                    </div>
                    <span class="section-icon">⌖</span>
                </div>

                <div class="package-grid">

                    <div class="info-box">
                        <div class="info-label">District</div>
                        <div class="info-value">
                            ${firstSource.garden.district}
                        </div>
                    </div>

                    <div class="info-box">
                        <div class="info-label">State</div>
                        <div class="info-value">
                            ${firstSource.garden.state}
                        </div>
                    </div>

                    <div class="info-box">
                        <div class="info-label">Garden Code</div>
                        <div class="info-value">
                            ${firstSource.garden.garden_code}
                        </div>
                    </div>

                    <div class="info-box">
                        <div class="info-label">Harvest Lot</div>
                        <div class="info-value">
                            ${firstSource.green_leaf.lot_code}
                        </div>
                    </div>

                </div>
            `;

            if (
                firstSource.garden.latitude !== null &&
                firstSource.garden.longitude !== null &&
                typeof firstSource.garden.latitude !== "undefined" &&
                typeof firstSource.garden.longitude !== "undefined"
            ) {

                const latitude = firstSource.garden.latitude;
                const longitude = firstSource.garden.longitude;

                const map = L.map("tea-map").setView(
                    [latitude, longitude],
                    13
                );

                L.tileLayer(
                    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                    {
                        attribution:
                            '&copy; OpenStreetMap contributors'
                    }
                ).addTo(map);

                L.marker([latitude, longitude])
                    .addTo(map)
                    .bindPopup(`
                        <strong>${firstSource.garden.name}</strong><br>
                        ${firstSource.garden.district},
                        ${firstSource.garden.state}
                    `)
                    .openPopup();
            }
        }

        let journeyHTML = `
            <div class="section-heading">
                <div>
                    <span class="eyebrow">PROVENANCE</span>
                    <h2>Your Tea's Journey</h2>
                </div>
                <span class="section-icon">↗</span>
            </div>

            <div class="journey-item">
                🌿 <strong>Green Leaf Harvest</strong>
                <p>
                    Lot:
                    ${firstSource?.green_leaf?.lot_code || "N/A"}
                </p>
            </div>

            <div class="journey-item">
                🏭 <strong>Factory Processing</strong>
                <p>
                    Batch:
                    ${firstSource?.factory?.batch_code || "N/A"}
                </p>
                <p>
                    ${firstSource?.factory?.factory_name || "N/A"}
                </p>
            </div>

            <div class="journey-item">
                🏬 <strong>Warehouse</strong>
                <p>
                    ${firstSource?.warehouse?.name || "N/A"}
                </p>
            </div>
        `;

        data.sources.forEach(source => {

            journeyHTML += `
                <div class="journey-item">
                    🔨 <strong>Auction</strong>

                    <p>
                        Lot:
                        ${source.auction_lot.code}
                    </p>

                    <p>
                        Quantity:
                        ${source.auction_lot.quantity_kg} kg
                    </p>

                    <p>
                        Grade:
                        ${source.auction_lot.grade || "N/A"}
                    </p>

                    <p>
                        Auction Centre:
                        ${source.auction_lot.auction_center || "N/A"}
                    </p>
                </div>
            `;
        });

        journeyHTML += `
            <div class="journey-item">
                🫖 <strong>Blending</strong>

                <p>
                    Blend:
                    ${data.blend.blend_code}
                </p>

                <p>
                    Tea Type:
                    ${data.blend.tea_type}
                </p>

                <p>
                    Output:
                    ${data.blend.output_quantity_kg} kg
                </p>
            </div>

            <div class="journey-item">
                📦 <strong>Packaging</strong>

                <p>
                    Package:
                    ${data.package.package_code}
                </p>

                <p>
                    ${data.package.number_of_packages} consumer packs
                </p>
            </div>
        `;

        journeySection.innerHTML = journeyHTML;

        const compliance = data.compliance;

        let complianceHTML = `
            <div class="section-heading">
                <div>
                    <span class="eyebrow">FOOD SAFETY</span>
                    <h2>Safety Verification</h2>
                </div>
                <span class="section-icon">✓</span>
            </div>

            <div class="compliance-status">
                <strong>
                    Overall Status:
                    ${compliance.overall_status}
                </strong>
            </div>
        `;

        compliance.tests.forEach(test => {

            if (test.result_status === "PASS") {

                complianceHTML += `
                    <div class="compliance-card pass">

                        <h3>
                            ✓ ${test.parameter_name}
                        </h3>

                        <p>
                            <strong>Status:</strong>
                            PASS
                        </p>

                        <p>
                            Within the applicable regulatory limit.
                        </p>

                        <p>
                            <strong>Limit:</strong>
                            ${test.maximum_allowed}
                            ${test.unit}
                        </p>

                        <p>
                            <strong>Rule source:</strong>
                            ${test.rule_source || "N/A"}
                        </p>

                    </div>
                `;

            } else if (test.result_status === "FAIL") {

                complianceHTML += `
                    <div class="compliance-card fail">

                        <h3>
                            ✕ ${test.parameter_name}
                        </h3>

                        <p>
                            <strong>Status:</strong>
                            FAIL
                        </p>

                        <p>
                            The result exceeds the applicable
                            configured compliance limit.
                        </p>

                        <p>
                            <strong>Limit:</strong>
                            ${test.maximum_allowed}
                            ${test.unit}
                        </p>

                        <p>
                            <strong>Rule source:</strong>
                            ${test.rule_source || "N/A"}
                        </p>

                    </div>
                `;

            } else if (test.result_status === "NOT_EVALUATED") {

                complianceHTML += `
                    <div class="compliance-card unknown">

                        <h3>
                            • ${test.parameter_name}
                        </h3>

                        <p>
                            <strong>Status:</strong>
                            NOT EVALUATED
                        </p>

                        <p>
                            No applicable compliance rule
                            was found for this parameter.
                        </p>

                    </div>
                `;

            } else if (test.result_status === "UNKNOWN") {

                complianceHTML += `
                    <div class="compliance-card unknown">

                        <h3>
                            • ${test.parameter_name}
                        </h3>

                        <p>
                            <strong>Status:</strong>
                            UNKNOWN
                        </p>

                        <p>
                            The available information is
                            insufficient for evaluation.
                        </p>

                    </div>
                `;

            } else if (test.result_status === "INCONCLUSIVE") {

                complianceHTML += `
                    <div class="compliance-card unknown">

                        <h3>
                            • ${test.parameter_name}
                        </h3>

                        <p>
                            <strong>Status:</strong>
                            INCONCLUSIVE
                        </p>

                        <p>
                            The test could not be conclusively
                            evaluated against the applicable rule.
                        </p>

                    </div>
                `;
            }
        });

        complianceSection.innerHTML = complianceHTML;

    } catch (error) {

        status.innerHTML = `
            <h2 class="error">
                Trace unavailable
            </h2>

            <p>
                ${error.message}
            </p>
        `;

        console.error("TeaTrace error:", error);
    }
}

loadTrace();