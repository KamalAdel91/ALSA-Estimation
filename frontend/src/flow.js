// The order an estimator builds an estimation in. Labels here are for the step buttons only;
// each screen's own title comes from the server.
export const FLOW = [
	{ key: "rfq", label: "RFQ", help: "What the customer asked for" },
	{ key: "scope", label: "Scope and crew", help: "Equipment, days and crew" },
	{ key: "rates", label: "Rates", help: "Salary and factor for each trade" },
	{ key: "accommodation", label: "Accommodation", help: "Housing for each trade" },
	{ key: "test_equipment", label: "Test equipment", help: "Test tools for the job" },
	{ key: "transportation", label: "Cars and fuel", help: "Cars, fuel and maintenance" },
	{ key: "other_costs", label: "Other costs", help: "Anything else, by budget category" },
	{ key: "supply", label: "Supply", help: "Items priced by Supply Chain" },
	{ key: "cost", label: "Margin and price", help: "Margin and the final price" },
];

export function stepRoute(estimation, key) {
	if (key === "rfq" || key === "cost" || key === "supply") return { name: key, params: { name: estimation } };
	return { name: "section", params: { name: estimation, section: key } };
}
