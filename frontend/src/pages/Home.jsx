import Dashboard  from "@/components/Dashboard/Dashboard";
import AlertPanel from "@/components/AlertPanel/AlertPanel";
import NetworkMap from "@/components/NetworkMap/NetworkMap";

export default function Home() {
  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div className="xl:col-span-2 space-y-6">
        <Dashboard />
        <NetworkMap />
      </div>
      <div>
        <AlertPanel />
      </div>
    </div>
  );
}
