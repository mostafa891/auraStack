import type { TypedSchema, TypedSchemaError } from "vee-validate";
import type { z } from "zod";

/**
 * محول مخصص لربط Zod v4 بـ VeeValidate.
 *
 * المكتبة الرسمية @vee-validate/zod لسه ما تدعمش Zod v4
 * فاحنا بنكتب الربط يدوياً — ده أبسط مما تتخيل:
 *
 * 1. VeeValidate بيبعت القيم (values) للـ validate()
 * 2. Zod بيعمل safeParse ويرجع نجاح أو أخطاء
 * 3. احنا بنحوّل أخطاء Zod لصيغة VeeValidate
 */
export function toTypedSchema<TOutput extends Record<string, unknown>>(
  zodSchema: z.ZodType<TOutput>
): TypedSchema<TOutput> {
  return {
    __type: "VVTypedSchema",

    async parse(values: Record<string, unknown>) {
      const result = zodSchema.safeParse(values);

      if (result.success) {
        return {
          value: result.data as TOutput,
          errors: [],
        };
      }

      // تحويل أخطاء Zod لصيغة VeeValidate
      const errors: TypedSchemaError[] = result.error.issues.map((issue) => ({
        path: issue.path.map(String).join(".") || issue.path[0]?.toString(),
        errors: [issue.message],
      }));

      return { errors };
    },
  };
}
