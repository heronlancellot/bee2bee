import { Brain } from "lucide-react";

import { LoginForm } from "@/components/login-form";
import { HexagonBackground } from "@/components/ui/hexagon-background";

export default function LoginPage() {
  return (
    <HexagonBackground
      hexagonSize={80}
      hexagonMargin={5}
      className="flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10"
    >
      <div className="flex w-full max-w-sm flex-col gap-6 relative z-10">
        <LoginForm />
      </div>
    </HexagonBackground>
  );
}
