# Glossary

Domain terms defined precisely. Use these definitions consistently in code, comments, and conversations.

---

## Electrical / NEC Domain

**AWG** — American Wire Gauge. The standard for wire conductor sizing in the US. Counterintuitively, lower numbers = larger wire (e.g., 4/0 AWG is larger than 12 AWG). Used in the `WireCableItem.awg` field.

**Ampacity** — The maximum continuous current a conductor can carry without exceeding its temperature rating, per NEC 310.15. Affected by ambient temperature and bundling.

**Area Classification** — Designation of hazardous locations per NEC Articles 500-516. Defines where explosion-proof equipment is required.
- *Class I* — flammable gases or vapors (oil & gas)
- *Class II* — combustible dust
- *Division 1* — hazardous under normal conditions
- *Division 2* — hazardous only under abnormal conditions
- *Zone 0/1/2* — IEC system (equivalent to Div 1/1/2)

**Bid Package** — The set of documents provided by a client for estimating purposes. May include one-lines, panel schedules, specs, area classification drawings, scope of work, and more.

**BOM** — Bill of Materials. A structured list of all materials needed for a project, with quantities, specifications, and confidence levels. The primary output of the electrical-estimator tool.

**Bundling Derating** — Reduction in allowable ampacity when multiple current-carrying conductors are installed together in a conduit or bundle. Per NEC Table 310.15(C)(1).

**Conduit Types:**
- *RGS* — Rigid Galvanized Steel. Heaviest, used in harsh environments.
- *IMC* — Intermediate Metal Conduit. Lighter than RGS, similar protection.
- *EMT* — Electrical Metallic Tubing. Thin-wall, indoor/dry locations.
- *PVC* — Polyvinyl Chloride. Non-metallic, used underground or in corrosive environments.

**Continuous Load** — A load expected to run for 3+ hours. Per NEC 210.19, conductors must be sized at 125% of the continuous load.

**DXF** — Drawing Exchange Format. AutoCAD's file format for electrical drawings (floor plans, one-lines). Supported by the `ezdxf` parser.

**Explosion-Proof** — Equipment rated for use in hazardous (classified) areas. Not explosion-proof in the literal sense — designed to contain any internal explosion without igniting the surrounding atmosphere.

**FLA** — Full Load Amps. The nameplate current draw of a motor at full rated load. Used for conductor and overcurrent device sizing.

**MCC** — Motor Control Center. A switchgear assembly containing motor starters, variable frequency drives, and control equipment. Appears in the "Panels, MCCs & Switchgear" BOM tab.

**NEC** — National Electrical Code. The US standard for safe electrical installation (NFPA 70). The 2023 edition is the reference for this tool's NEC tables.

**NEMA Rating** — National Electrical Manufacturers Association enclosure rating. Defines protection level (e.g., NEMA 4X = watertight + corrosion-resistant).

**One-Line Diagram** — A simplified electrical diagram showing the power distribution system as a single line. Key source document for extracting panel, transformer, and cable data.

**Panel Schedule** — A tabular document listing each circuit in a panel board, with breaker size, load description, and amperage. Primary source for `PanelItem` and `CircuitItem` extraction.

**Scope of Work** — Document describing what work is included in the project. Used to validate that extracted items are in-scope.

**Trade Size** — The nominal size of conduit (e.g., "1-inch", "2-inch"). Not the actual diameter — a 1-inch conduit has an inner diameter of approximately 1.049 inches.

**VFD** — Variable Frequency Drive. Electronic device controlling motor speed. May appear in panel schedules or MCCs.

---

## AI / Extraction Domain

**Chunk** — A portion of a document's text sent to the AI in a single API call. Sized at ~6,000 tokens with 1,000-token overlap between chunks to preserve context across boundaries.

**Confidence Level** — The tool's certainty about an extracted value. Three levels:
- *Confirmed* — Directly stated in the source document
- *Estimated* — Calculated or inferred from related data
- *Assumed* — No source data; a default value was applied

**Extraction** — The AI process of reading a document chunk and returning structured data matching the BOM schema.

**Flag** — An `AssumptionFlag` record attached to a BOM item indicating uncertainty, a missing value, or a NEC compliance concern. Appears in the "Assumptions & Flags" BOM tab.

**MD5 Cache** — The disk-based cache in `.cache/` that stores AI responses keyed by MD5 hash of (prompt + chunk content). Prevents redundant API calls.

**Prompt** — The instruction text sent to Claude to guide extraction. Consists of a system prompt (persona + rules) and a user prompt (document chunk + extraction instructions).

**Token Budget** — The maximum number of tokens allocated to a single AI call. Set in `config/settings.py`. Prevents runaway costs on large documents.

---

## Finance / Stock Screener Domain

**DCF** — Discounted Cash Flow. A valuation method estimating the present value of a company's future free cash flows. The primary valuation model in the stock screener.

**EV/EBITDA** — Enterprise Value divided by Earnings Before Interest, Taxes, Depreciation, and Amortization. A valuation multiple less affected by capital structure than P/E.

**FCF** — Free Cash Flow. Operating cash flow minus capital expenditures. A purer measure of a company's cash generation than net income.

**PEG Ratio** — Price/Earnings to Growth ratio. P/E divided by expected earnings growth rate. Accounts for growth in the valuation.

**ROIC** — Return on Invested Capital. Net operating profit after tax divided by invested capital. A quality metric indicating how efficiently a company uses its capital.

**Terminal Growth Rate** — The assumed long-term growth rate of a company's FCF beyond the DCF projection period. Set at 3% in the screener (approximately GDP growth).

**Value Trap** — A stock that appears cheap by metrics but is cheap for a reason (declining business, poor management). The quality metrics (ROE, ROIC) in the screener are designed to filter these out.

**WACC** — Weighted Average Cost of Capital. The discount rate used in DCF valuation, representing the opportunity cost of capital. Set at 10% in the screener.
