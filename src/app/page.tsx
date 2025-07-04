import { ContactLinks } from "@/components/ContactLinks";
import Image from "next/image";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="max-w-4xl mx-auto text-center">
        <div className="mb-8">
          <Image
            src="/images/writing-illustration.png"
            alt="Writing and literature"
            width={400}
            height={300}
            className="mx-auto"
            priority
          />
        </div>
        
        <ContactLinks />
      </div>
    </main>
  );
}