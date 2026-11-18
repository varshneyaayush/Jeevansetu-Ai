const roles = [
  { t: "Bystander", d: "Login-free Emergency SOS: GPS, AI triage, hospital match, live dispatch, break-glass." },
  { t: "Patient", d: "Symptom-to-department matching, appointment booking, Medical Memory with OCR and RAG." },
  { t: "Hospital Admin", d: "Live command center: capacity, diversion, incoming pre-alerts, audit trail." },
  { t: "Family Manager", d: "Consent matrix and authorised live updates during an emergency." },
];

const modules = [
  ["Haversine + weighted scoring", "0.35 facilities, 0.25 distance, 0.20 beds, 0.20 workload"],
  ["Rules + NLP triage", "Severity, required facilities, first-aid steps"],
  ["Simulated OCR", "Medicines, dosages, vitals and lab values"],
  ["Hybrid RAG", "Synonym-expanded TF-IDF with cited sources"],
  ["Audit log", "SHA-256 hash chain, break-glass highlighted"],
  ["Consent control", "Doctors, Ambulance Responders, Hospitals"],
];

export default function App() {
  return (
    <div className="min-h-screen bg-[#F5EFE6] text-[#1B2B21]">
      <header className="mx-auto max-w-5xl px-6 pt-10">
        <div className="rounded-2xl border-b-4 border-[#8B5CF6] bg-[#1F3D2B] p-8 text-[#E8DCC4]">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#bfae88]">
            Roboforge Hackathon 2026 | Software &amp; Intelligent Systems | Healthcare AI
          </p>
          <h1 className="mt-2 font-serif text-5xl font-bold text-[#F5EFE6]">JeevanSetu AI</h1>
          <span className="mt-4 inline-block rounded-full bg-[#2F7A55] px-4 py-1.5 font-bold text-white">
            A place where minutes don&apos;t cost lives.
          </span>
          <p className="mt-5 text-sm">Built by Team Optimove: Aayush Varshney, Sonali, Aksha Malik, Diksha Kalia</p>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-10 px-6 py-10">
        <section>
          <h2 className="mb-3 font-serif text-2xl font-bold text-[#1F3D2B]">The prototype is a Streamlit app</h2>
          <p className="mb-4 text-[#5C6B61]">
            The full interactive demo lives in <code className="rounded bg-[#E8DCC4] px-1.5 py-0.5">app.py</code> (single file,
            simulated data, no API keys). Run it locally or deploy it on Streamlit Cloud:
          </p>
          <pre className="overflow-x-auto rounded-xl bg-[#1F3D2B] p-4 text-sm text-[#E8DCC4]">
{`pip install -r requirements.txt
streamlit run app.py`}
          </pre>
        </section>

        <section>
          <h2 className="mb-3 font-serif text-2xl font-bold text-[#1F3D2B]">Four role views</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {roles.map((r) => (
              <div key={r.t} className="rounded-xl border-[1.5px] border-[#1F3D2B] bg-[#FFFCF6] p-5">
                <h3 className="font-serif text-lg font-bold text-[#1F3D2B]">{r.t}</h3>
                <p className="mt-1 text-sm text-[#5C6B61]">{r.d}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="mb-3 font-serif text-2xl font-bold text-[#1F3D2B]">Under the hood</h2>
          <div className="grid gap-3 sm:grid-cols-3">
            {modules.map(([t, d]) => (
              <div key={t} className="rounded-xl bg-[#1F3D2B] p-4 text-[#E8DCC4]">
                <div className="font-bold text-[#C4B5FD]">{t}</div>
                <div className="mt-1 text-sm">{d}</div>
              </div>
            ))}
          </div>
        </section>

        <div className="rounded-xl border-2 border-[#DC2626] border-l-[10px] bg-[#FEF2F2] p-4 text-sm text-[#7F1D1D]">
          Prototype: hospital availability, workload and ambulance tracking use simulated data. Not medical advice.
        </div>
      </main>
    </div>
  );
}
