import ThreatStats from "@/components/ThreatStats/ThreatStats";
import NetworkMap  from "@/components/NetworkMap/NetworkMap";

export default function Analytics() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ThreatStats />
      <NetworkMap />
    </div>
  );
}
