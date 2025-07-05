import { ContactLinks } from "@/components/ContactLinks";
import Image from "next/image";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-8">
      <div className="max-w-5xl mx-auto text-center">
        <div className="mb-12">
          <Image
            src="/images/Shutterstock 650735719.jpg"
            alt="Modern workspace with laptop, phone, and professional tools"
            width={700}
            height={467}
            className="mx-auto rounded-xl shadow-2xl border border-neutral/20"
            priority
          />
        </div>
        
        <div className="bg-white/80 backdrop-blur-sm rounded-lg px-8 py-6 shadow-lg border border-neutral/10">
          <ContactLinks />
        </div>
      </div>
    </main>
  );
}